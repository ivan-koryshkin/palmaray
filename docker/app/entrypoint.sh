#!/bin/sh
set -e

pipenv run alembic upgrade head
exec python main.py