SHELL := /bin/bash

# React
watch:
	rm -rf client/dist
	pushd client && npm install && npm start

# Postgres
shell:
	docker-compose build core
	docker-compose run --rm core bash

revision:
	docker-compose run --rm core alembic revision --autogenerate -m "$(msg)"

migration:
	docker-compose run --rm core alembic upgrade head

setup:
	docker-compose build postgres
	docker-compose up -d postgres
	docker-compose run --rm core alembic upgrade head
	docker-compose stop core

clean:
	docker stop seamless-web_postgres_1
	docker rm seamless-web_postgres_1
	docker rmi seamless-web_core
	docker rmi $(docker images -f dangling=true -aq)