MANAGE := poetry run python3 manage.py

install:
	poetry install

migrate:
	${MANAGE} migrate

start:
	${MANAGE} runserver

lint:
	poetry run flake8 .

superuser:
	${MANAGE} createsuperuser
