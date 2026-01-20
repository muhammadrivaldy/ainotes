.PHONY: help install run dev clean clean-db clean-all test lint format

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    - Create venv and install dependencies"
	@echo "  make run        - Run the FastAPI server"
	@echo "  make dev        - Run the server with auto-reload"
	@echo "  make clean      - Remove Python cache files"
	@echo "  make clean-db   - Remove database files (chat history and vector store)"
	@echo "  make clean-all  - Remove everything (cache, db, venv)"
	@echo "  make test       - Run tests (if available)"
	@echo "  make lint       - Check code style"
	@echo "  make format     - Format code with black"

# Install dependencies
install:
	@echo "Creating virtual environment..."
	python3 -m venv .venv
	@echo "Installing dependencies..."
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "Done! Activate with: source .venv/bin/activate"

# Run the server
run:
	@echo "Starting FastAPI server..."
	.venv/bin/python main.py

# Run with auto-reload for development
dev:
	@echo "Starting FastAPI server with auto-reload..."
	.venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Clean Python cache files
clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cache cleaned!"

# Clean database files
clean-db:
	@echo "Removing database files..."
	rm -rf database/chroma/
	rm -f database/chat_history.db
	@echo "Database files removed!"

# Clean everything including venv
clean-all: clean clean-db
	@echo "Removing virtual environment..."
	rm -rf .venv
	@echo "Everything cleaned!"

# Run tests (placeholder - add your test framework)
test:
	@echo "Running tests..."
	.venv/bin/pytest tests/ -v || echo "No tests found. Add tests in tests/ directory"

# Lint with flake8 (install first: pip install flake8)
lint:
	@echo "Checking code style..."
	.venv/bin/flake8 . --exclude=.venv,__pycache__ --max-line-length=120 || echo "Install flake8: pip install flake8"

# Format code with black (install first: pip install black)
format:
	@echo "Formatting code..."
	.venv/bin/black . --exclude=.venv || echo "Install black: pip install black"
