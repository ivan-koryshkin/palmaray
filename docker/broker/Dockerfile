FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev git \
    && rm -rf /var/lib/apt/lists/*

# wheel is built by `make wheel` into dist/
COPY dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

CMD ["palmaray-broker"]
