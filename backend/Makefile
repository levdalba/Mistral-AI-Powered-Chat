# Makefile for Mistral AI Chat Backend
# Provides common development tasks and commands

.PHONY: help install dev test lint format clean docker-build docker-run

# Default target
help:
	@echo "Mistral AI Chat Backend - Available Commands:"
	@echo ""
	@echo "  setup      - Create virtual environment and install dependencies"
	@echo "  install    - Install dependencies (requires active venv)"
	@echo "  dev        - Start development server with hot reload"
	@echo "  test       - Run all tests"
	@echo "  lint       - Run linting (flake8, mypy)"
	@echo "  format     - Format code (black, isort)"
	@echo "  clean      - Clean up temporary files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run - Run Docker container"
	@echo ""

# Setup virtual environment
setup:
	@echo "🚀 Setting up virtual environment..."
	python3 -m venv venv
	@echo "✅ Virtual environment created"
	@echo "Please activate it with: source venv/bin/activate"
	@echo "Then run: make install"

# Install dependencies
install:
	@echo "📥 Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Start development server
dev:
	@echo "🔥 Starting development server..."
	uvicorn app.main:app --reload --port 8000

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest

# Run tests with coverage
test-coverage:
	@echo "🧪 Running tests with coverage..."
	pytest --cov=app tests/

# Lint code
lint:
	@echo "🔍 Running linting..."
	flake8 app/
	mypy app/

# Format code
format:
	@echo "🎨 Formatting code..."
	black app/
	isort app/

# Clean temporary files
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Docker commands
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t mistral-chat-backend .

docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p 8000:8000 --env-file .env mistral-chat-backend

# Development with hot reload
watch:
	@echo "👀 Starting development server with file watching..."
	uvicorn app.main:app --reload --reload-dir app --port 8000
