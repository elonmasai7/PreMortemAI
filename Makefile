PYTHON ?= python3

.PHONY: install run test lint format check-env validate-splunk export-openapi

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) scripts/run_dev.py

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff check . --fix

check-env:
	$(PYTHON) scripts/check_environment.py

validate-splunk:
	$(PYTHON) scripts/validate_splunk_connection.py

export-openapi:
	$(PYTHON) scripts/export_openapi.py
