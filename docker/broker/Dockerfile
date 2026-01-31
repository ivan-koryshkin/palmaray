FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pipenv
COPY Pipfile Pipfile.lock* /app/
ENV PIPENV_NOSPIN=1
RUN pipenv install --deploy --system || pipenv install --system --skip-lock
COPY . /app

CMD ["python", "-m", "broker"]
