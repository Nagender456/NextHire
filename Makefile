PYTHON := $(shell if test -x backend/.venv/bin/python; then echo backend/.venv/bin/python; else echo python3; fi)

.PHONY: test lint format-check

test:
	$(PYTHON) -m pytest backend/tests
	cd frontend && npm test -- --run

lint:
	$(PYTHON) -m ruff check backend
	cd frontend && npm run lint

format-check:
	$(PYTHON) -m ruff format --check backend
