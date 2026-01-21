.PHONY: help install dev test clean docker-build docker-up docker-down init-db scrape-templates run

help:
	@echo "Chisom.ai - Available Commands"
	@echo "================================"
	@echo "install          - Install dependencies"
	@echo "dev              - Run in development mode"
	@echo "test             - Run tests"
	@echo "clean            - Clean temporary files"
	@echo "docker-build     - Build Docker images"
	@echo "docker-up        - Start Docker containers"
	@echo "docker-down      - Stop Docker containers"
	@echo "init-db          - Initialize database"
	@echo "scrape-templates - Scrape code templates"
	@echo "run              - Run the application"
	@echo "format           - Format code"
	@echo "lint             - Lint code"

install:
	pip install -r requirements.txt
	npm install -g eslint prettier

dev:
	chainlit run app.py --watch

test:
	pytest tests/ -v --cov=. --cov-report=html

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf build dist *.egg-info

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

init-db:
	python cli.py init

scrape-templates:
	python cli.py scrape-templates

create-user:
	python cli.py create-user

upgrade-user:
	python cli.py upgrade-user

stats:
	python cli.py stats

run:
	chainlit run app.py --host 0.0.0.0 --port 8000

format:
	black .
	npx prettier --write "**/*.{js,jsx,ts,tsx,json,md}"

lint:
	ruff check .
	npx eslint "**/*.{js,jsx,ts,tsx}"

setup: install init-db
	@echo "✅ Setup complete! Run 'make run' to start the application."
