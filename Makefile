# dont confuse these commands for real files
.PHONY: help install seed migrations test dev prod

# default target when I run "make" without arguments
.DEFAULT_GOAL: help

help:
	@echo "------------------------------------------------------------------"
	@echo " FastAPI Primer                                                   "
	@echo "------------------------------------------------------------------"
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help           : Show this help message."
	@echo "  install        : Install dependecies in requirements.txt file."
	@echo "  seed           : Run seed database scripts."
	@echo "  migrations     : Run database migrations with alembic."
	@echo "  test           : Run the pytest test suite."
	@echo "  dev            : Run app in development environment."
	@echo "  prod           : Run app in production environment."
	@echo "------------------------------------------------------------------"

install:
	@echo "Installing project dependecies..."
	pip install -r requirements.txt

seed: install
	@echo "Running application seed database script..."
	python -m scripts.seed

migrations: seed
	@echo "Running project migrations with alembic..."
	alembic upgrade head

test:
	@echo "Running project tests..."
	pytest tests/ -v

# run server in development environment, with live reload and logging
dev:
	@echo "Starting local development server..."
	fastapi dev src/main.py

# run server in production environment, no live reload
prod:
	@echo "Starting production server..."
	fastapi run src/main.py
