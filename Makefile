PYTHON ?= python3

.PHONY: install run worker migrate test lint format check-env validate-splunk export-openapi backup-db restore-db

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) scripts/run_dev.py

worker:
	$(PYTHON) scripts/run_worker.py

migrate:
	$(PYTHON) scripts/run_migrations.py

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

backup-db:
	$(PYTHON) scripts/backup_postgres.py

restore-db:
	$(PYTHON) scripts/restore_postgres.py
