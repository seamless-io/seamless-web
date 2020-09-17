SHELL := /bin/bash

shell:
	docker-compose run --rm migration bash

revision:
	docker-compose run --rm migration alembic revision --autogenerate -m "$(msg)"

migration:
	docker-compose run --rm migration alembic upgrade head

down-migration:
	docker-compose run --rm migration alembic downgrade -1

unit-test:
	pytest -v tests/unit

integration-test:
	PYTHONPATH=. pytest -v tests/integration

test:
	PYTHONPATH=. pytest -v tests

setup-db:
	docker-compose build postgres
	docker-compose up -d postgres
	docker-compose run --rm migration alembic upgrade head
	docker-compose stop migration

clean-db:
	docker stop seamless-web_postgres_1
	docker rm seamless-web_postgres_1
	docker rmi seamless-web_migration
	docker rmi $(docker images -f dangling=true -aq)