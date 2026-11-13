PYTHON ?= python3
IMAGE_TAG ?= latest
DIST_DIR := dist

.PHONY: help wheel clean docker docker-app docker-broker up down format check

help:
	@echo "make wheel         - build wheel into $(DIST_DIR)/"
	@echo "make docker        - build wheel, then app and broker docker images"
	@echo "make up / down     - docker compose up --build / down"
	@echo "make format/check  - isort+ruff+black / ruff+mypy"
	@echo "make clean         - remove build artifacts"

wheel: clean
	$(PYTHON) -m pip wheel --no-deps --wheel-dir $(DIST_DIR) .
	@ls -1 $(DIST_DIR)/*.whl

clean:
	rm -rf build $(DIST_DIR) *.egg-info

docker: docker-app docker-broker

docker-app: wheel
	docker build -f docker/app/Dockerfile -t palmaray-app:$(IMAGE_TAG) .

docker-broker: wheel
	docker build -f docker/broker/Dockerfile -t palmaray-broker:$(IMAGE_TAG) .

up: wheel
	docker compose up --build -d

down:
	docker compose down

format:
	isort . && ruff check --fix . && black .

check:
	ruff check . && mypy .
