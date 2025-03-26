PYTHON := python3
POETRY := poetry
BUILD_DIR := .build

.PHONY: clean dev validate install build synth deploy destroy test test-unit test-integration

.ONESHELL:  # run all commands in a single shell, ensuring it runs within a local virtual env
clean:
	rm -rf $(BUILD_DIR)

dev:
	pip install --upgrade pip pre-commit poetry
	pre-commit install
# ensures poetry creates a local virtualenv (.venv)
	poetry config --local virtualenvs.in-project true
	poetry install --no-root

validate:
	pre-commit run --all-files

install:
	$(POETRY) install

build:
	mkdir -p $(BUILD_DIR)/lambda
	rm -rf $(BUILD_DIR)/lambda/*
	rsync -av --exclude '__pycache__' service/ $(BUILD_DIR)/lambda/service/
	mkdir -p $(BUILD_DIR)/layer
	$(POETRY) export --without-hashes --without=dev --format=requirements.txt > $(BUILD_DIR)/layer/requirements.txt

test:
	$(POETRY) run pytest tests/

# Executa apenas os testes de unidade
test-unit:
	$(POETRY) run pytest tests/drink/unit/ -v

# Executa apenas os testes de integração
test-integration:
	$(POETRY) run pytest tests/drink/integration/ -v -m integration

synth: build
	$(POETRY) run cdk synth

deploy: build
	$(POETRY) run cdk deploy

destroy:
	$(POETRY) run cdk destroy

.PHONY: test-only
test-only: test
