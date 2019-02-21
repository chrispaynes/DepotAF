.PHONY: airflowAttach airflowDBClean buildAirflow postgresImage postgresClean

# sudo to override permission errors on mounted PostgreSQL docker volume
buildAirflow:
	sudo docker-compose build airflow-app

postgresImage: postgresClean
	docker-compose kill postgres \
	&& docker rmi postgres_depot:latest | true \
	&& sudo docker-compose build postgres \
	&& docker-compose up -d --force-recreate \
	&& docker-compose logs -f postgres

postgresClean:
	sudo rm -rf ./pgdata

airflowDBClean:
	sudo rm -rf ./pgdata_airflow

airflowAttach:
	docker exec -ti airflow-app bash

DAG=notecard_populator
TASK=populate_csv
airflowTest:
	docker exec -ti airflow-app airflow test $(DAG) $(TASK) 01-01-01