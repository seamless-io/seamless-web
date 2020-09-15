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
