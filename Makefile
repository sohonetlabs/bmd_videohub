.PHONY: help install lint format check test clean

help:
	@echo "Available commands:"
	@echo "  make install    - Create venv and install dependencies"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with ruff"
	@echo "  make check      - Run both lint and format check"
	@echo "  make test       - Run tests (when implemented)"
	@echo "  make clean      - Remove virtual environment and cache files"

install:
	python3 -m venv venv
	./venv/bin/pip install -r requirements/requirements.txt
	./venv/bin/pip install ruff

lint:
	./venv/bin/ruff check .

format:
	./venv/bin/ruff format .

check: lint
	./venv/bin/ruff format --check .

test:
	@echo "No tests implemented yet"
	# When tests are added:
	# ./venv/bin/pytest

clean:
	rm -rf venv
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete