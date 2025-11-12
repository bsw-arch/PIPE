# Makefile for PIPE Domain Bot System

.PHONY: help install test lint format clean docker-build docker-run

help:
	@echo "PIPE Domain Bot System - Makefile Commands"
	@echo "==========================================="
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run with Docker Compose"
	@echo "  make run           - Run bot system locally"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	pylint src/ --disable=C0111,R0903 || true
	mypy src/ --ignore-missing-imports || true

format:
	black src/ tests/
	@echo "Code formatted successfully!"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	rm -rf build/ dist/ *.egg-info
	@echo "Cleaned build artifacts!"

docker-build:
	docker build -t pipe-bots:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

run:
	python -m src.main

dev-setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Development environment set up!"
	@echo "Activate with: source venv/bin/activate"
