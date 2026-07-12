# Makefile for Hashnode MCP Server

.PHONY: setup install test run clean

# Default Python interpreter
PYTHON := python
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

# Setup virtual environment and install dependencies
setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	$(PIP) install pytest pytest-asyncio

# Install the package
install:
	$(PIP) install -e .

# Install test dependencies
test-deps:
	$(PIP) install pytest pytest-asyncio

# Run tests
test:
	$(PYTEST) -v tests/

# Run the server
run:
	$(PYTHON) run_server.py

# Clean up generated files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
