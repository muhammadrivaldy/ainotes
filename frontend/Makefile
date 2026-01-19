.PHONY: help install dev build preview lint format clean check-backend start stop

# Default target
help:
	@echo "AI Notes Frontend - Available commands:"
	@echo ""
	@echo "  make install        - Install dependencies"
	@echo "  make dev            - Start development server"
	@echo "  make build          - Build for production"
	@echo "  make preview        - Preview production build"
	@echo "  make lint           - Run ESLint"
	@echo "  make format         - Format code with Prettier"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make check-backend  - Check if backend is running"
	@echo "  make start          - Install deps and start dev server"
	@echo "  make stop           - Stop all node processes (use with caution)"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	npm install

# Start development server
dev:
	@echo "Starting development server on http://localhost:5173..."
	npm run dev

# Build for production
build:
	@echo "Building for production..."
	npm run build

# Preview production build
preview:
	@echo "Previewing production build..."
	npm run preview

# Run linter
lint:
	@echo "Running ESLint..."
	npm run lint

# Format code with Prettier
format:
	@echo "Formatting code with Prettier..."
	npx prettier --write "src/**/*.{js,jsx,css}"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist node_modules/.vite

# Deep clean (including node_modules)
clean-all:
	@echo "Deep cleaning (removing node_modules and build artifacts)..."
	rm -rf dist node_modules package-lock.json

# Check if backend is running
check-backend:
	@echo "Checking if backend is running on http://localhost:8000..."
	@curl -s http://localhost:8000/ > /dev/null && echo "✓ Backend is running" || echo "✗ Backend is NOT running. Please start it first."

# Quick start (install + dev)
start: install
	@echo "Starting development server..."
	npm run dev

# Stop development server
stop:
	@echo "Stopping Node.js processes..."
	@pkill -f "vite" || echo "No Vite processes found"

# Reinstall dependencies
reinstall: clean-all install
	@echo "Dependencies reinstalled successfully"
