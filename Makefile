setup:
	pre-commit install

run-dev:
	APP_ENV=dev uvicorn app.main:app --reload

db-run:
	docker run \
		--rm   \
		--name pgdb \
		-p 5432:5432 \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_PASSWORD=postgres \
		-e POSTGRES_DB=rwdb \
		-d postgres:14.0-alpine

db-down: db-stop
	docker rm pgdb

db-start:
	docker start pgdb

db-stop:
	docker stop pgdb

db-shell:
	docker exec -it pgdb psql -U postgres

db-migrate-dev:
	APP_ENV=dev alembic upgrade head

db-run-test:
	docker run \
		--rm \
		--name pgdb-test \
		--env-file test.env \
		-p 5433:5432 \
		-d postgres:14.0-alpine

check-db:
	while ! nc -z localhost 5432; do sleep 0.1; done

run-test:
	pytest
