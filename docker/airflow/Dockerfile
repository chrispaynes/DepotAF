FROM puckel/docker-airflow

RUN pip install psycopg2-binary --user

ADD ./docker/airflow/airflow.cfg /usr/local/airflow/airflow.cfg

COPY ./dags /usr/local/airflow/dags