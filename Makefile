# dont confuse these commands for real files
.PHONY: help install seed migrations test dev prod

# default target when I run "make" without arguments
.DEFAULT_GOAL: help
PROJECT=FastAPI Primer Makefile

help: ## Show this help message
	@command -v awk >/dev/null 2>&1 || { \
		printf >&2 '%s\n' "awk not found. Install gawk: https://www.gnu.org/software/gawk/"; \
		exit 1; \
	}
	@awk 'BEGIN { \
			FS = ":.*##"; \
			printf "$(PROJECT)\n"; \
			printf "\nUsage:\n  make \033[36m<target>\033[0m\n\n"; \
		} \
		/^##@/ { \
			line = $$0; \
			sub(/^##@[ \t]*/, "", line); \
			printf "\n\033[1m%s\033[0m\n", line; \
			next; \
		} \
		/^[a-zA-Z0-9_%\/.$$()-]+:.*##/ { \
			found = 1; \
			desc = $$2; \
			gsub(/^[ \t]+|[ \t]+$$/, "", desc); \
			printf "  \033[36m%-24s\033[0m %s\n", $$1, desc; \
		} \
		END { if (!found) printf "  (no documented targets)\n"; }' \
		$(MAKEFILE_LIST)

install: ## Install project dependencies from requirements.txt file
	@echo "Installing project dependecies..."
	pip install -r requirements.txt

seed: install ## Seed application database 
	@echo "Running application seed database script..."
	python -m scripts.seed

migrations: install ## Run database migrations with alembic
	@echo "Running project migrations with alembic..."
	alembic upgrade head

test: ## Run application test suite with pytest
	@echo "Running project tests..."
	pytest tests/ -v

dev: ## Run local development server with live reload
	@echo "Starting local development server..."
	fastapi dev src/main.py

prod: ## Run production server
	@echo "Starting production server..."
	fastapi run src/main.py
