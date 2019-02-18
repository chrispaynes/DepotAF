.PHONY: buildAirflow databaseImage databaseClean 

# sudo to override permission errors on mounted PostgreSQL docker volume
buildAirflow:
	sudo docker-compose build airflow-app

databaseImage: databaseClean
	docker-compose build postgres

databaseClean:
	sudo rm -rf ./docker/postgres/pgdata

