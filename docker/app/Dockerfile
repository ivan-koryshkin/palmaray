FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pipenv
COPY Pipfile Pipfile.lock* /app/
RUN pipenv install --system --skip-lock || pipenv install --system --skip-lock
COPY . /app
RUN pipenv run alembic upgrade head
CMD ["python", "main.py"]
