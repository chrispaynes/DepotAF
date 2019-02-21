from airflow import DAG
from airflow.operators import PythonOperator, TriggerDagRunOperator, BaseSensorOperator, PostgresOperator
from datetime import datetime, timedelta
from airflow.models import Variable
import psycopg2 as pg
import os
import re
import csv
import shutil

from datetime import datetime
from airflow.models import BaseOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults

class OmegaFileSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(self, filepath, filepattern, *args, **kwargs):
        super(OmegaFileSensor, self).__init__(*args, **kwargs)
        self.filepath = filepath
        self.filepattern = filepattern

    def poke(self, context):
        file_pattern = re.compile(self.filepattern)

        for index, file in enumerate(os.listdir(self.filepath)):
            context['task_instance'].xcom_push(key="file", value=file)
            if not re.search(file_pattern, file):
                return False
            else:
                print(f'Sensing new file {self.filepattern} file "{file}"')
                context['task_instance'].xcom_push(key="file", value=file)
                return True


class OmegaPlugin(AirflowPlugin):
    name = "omega_plugin"
    operators = [OmegaFileSensor]

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2017, 6, 26),
    'provide_context': True,
    'retries': 0,
    'retry_delay': timedelta(seconds=1)
}

task_name = 'detect_notecard_csv'
# defined in Admin -> Variables
filepath = Variable.get("source_path")
destination = Variable.get("destination_path")
filepattern = Variable.get("file_pattern")

dag = DAG(
    'notecard_populator',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    max_active_runs=2,
    concurrency=8)

sensor_task = OmegaFileSensor(
    task_id=task_name,
    filepath=filepath,
    filepattern=filepattern,
    poke_interval=60,
    timeout=3600,
    dag=dag)

def populate_db(**context):
    print("POPULATING THE DB")

    file = context['task_instance'].xcom_pull(key="file", task_ids=task_name)
    # file = "Progress - Flashcards.csv"

    if (file is None):
        return

    conn = pg.connect(f'host={Variable.get("pg_host")} dbname={Variable.get("pg_db_name")} user={Variable.get("pg_host")} password={Variable.get("pg_host")}')

    with open(os.path.join(filepath, file)) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # advance the iterator to skip the header line
        next(reader)

        for row in reader:
            print("ROW =>", row)
            if not row[1] or row[1] is None or not row[3] or row[3] is None:
                continue

            cur = conn.cursor()
            sql = """
            insert into alpha.notecard (question, answer) values(%s, %s)
            on conflict do nothing
            returning notecard_id
            """

            cur.execute(sql, (row[1], row[2] if row[2] is not None else ''))

            res = cur.fetchone()

            if res is not None and len(res) > 0:
                notecard_id = res[0]

                for tag in row[3:5]:
                    sql = """
                        insert into alpha.category (category_name)
                        values(initcap(%s))
                        on conflict (category_name)
                        do update
                        set category_name=alpha.category.category_name
                        returning category_id
                    """

                    if not tag:
                        continue

                    cur.execute(sql, (tag,))

                    res = cur.fetchone()

                    if res is not None and len(res) > 0:
                        category_id = res[0]

                        sql = """
                            insert into alpha.notecard_categories (notecard_id, category_id)
                            values (%s,%s)
                        """

                        cur.execute(sql, (notecard_id, category_id))
                        conn.commit()

    # move file to process folder upon completion
    shutil.move(os.path.join(filepath, file), os.path.join(destination, file))

    return True

populate_task = PythonOperator(
    task_id='populate_csv',
    provide_context=True,
    depends_on_past=True,
    python_callable=populate_db,
    dag=dag)

# trigger = TriggerDagRunOperator(
#     task_id='trigger_dag_rerun',
#     trigger_dag_id=task_name,
#     dag=dag)

populate_task.set_upstream(sensor_task)