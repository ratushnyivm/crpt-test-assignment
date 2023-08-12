MANAGE := poetry run python3 manage.py

install:
	poetry install

start:
	${MANAGE} runserver

lint:
	poetry run flake8 .
