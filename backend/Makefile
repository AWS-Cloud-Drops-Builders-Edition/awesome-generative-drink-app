# Makefile for backend application

# Variables
PYTHON := python3
PIP := pip
POETRY := poetry
BUILD_DIR := .build

# Targets
.PHONY: clean install build synth deploy destroy test

clean:
	rm -rf $(BUILD_DIR)

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

deploy: synth
	$(POETRY) run cdk deploy

destroy: 
	$(POETRY) run cdk destroy

.PHONY: test-only
test-only: test