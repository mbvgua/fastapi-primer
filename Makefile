.PHONY: all install test dev prod

# deafult target when you just run make
all: install test prod

install:
	@echo "Installing project dependecies..."
	pip install --pre mariadb
	pip install -r requirements.txt
	alembic upgrade head
	python ./populate_db.py

# run tests
test:
	@echo "Running project tests..."
	pytest tests/ -v

# run server in development environment, with live reload and logging
dev:
	@echo "Starting local development server..."
	fastapi dev

# run server in production environment, no live reload
prod:
	@echo "Starting production server..."
	fastapi run
