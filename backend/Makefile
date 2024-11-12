PYTHON := python3
POETRY := poetry
BUILD_DIR := .build

.PHONY: clean dev precommit install build synth deploy destroy test

.ONESHELL:  # run all commands in a single shell, ensuring it runs within a local virtual env
clean:
	rm -rf $(BUILD_DIR)

dev:
	pip install --upgrade pip pre-commit poetry
	pre-commit install
# ensures poetry creates a local virtualenv (.venv)
	poetry config --local virtualenvs.in-project true
	poetry install --no-root

precommit:
	pre-commit run --all-files

install:
	$(POETRY) install

build:
	mkdir -p $(BUILD_DIR)/lambda
	cp lambda/*.py $(BUILD_DIR)/lambda/
	mkdir -p $(BUILD_DIR)/layer
	$(POETRY) export --without-hashes --without=dev --format=requirements.txt | grep -v "^\s*#" | grep -v "^-e" > $(BUILD_DIR)/layer/requirements.txt

test:
	$(POETRY) run pytest tests/

synth: build
	$(POETRY) run cdk synth

deploy: build
	$(POETRY) run cdk deploy

destroy:
	$(POETRY) run cdk destroy

.PHONY: test-only
test-only: test
