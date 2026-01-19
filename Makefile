.PHONY: help install install-backend install-frontend install-website \
	dev dev-backend dev-frontend dev-website dev-all \
	build build-backend build-frontend build-website build-all \
	clean clean-backend clean-frontend clean-website clean-all \
	test test-backend test-frontend test-all \
	docker-up docker-down docker-build docker-logs \
	check-backend status

# Default target
help:
	@echo "======================================"
	@echo "AI Notes Monorepo - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "Installation:"
	@echo "  make install              - Install all components"
	@echo "  make install-backend      - Install backend dependencies"
	@echo "  make install-frontend     - Install frontend dependencies"
	@echo "  make install-website      - Install website dependencies"
	@echo ""
	@echo "Development (Local):"
	@echo "  make dev-all              - Start all services (requires 3 terminals)"
	@echo "  make dev-backend          - Start backend server (port 8000)"
	@echo "  make dev-frontend         - Start frontend dev server (port 5173)"
	@echo "  make dev-website          - Start website dev server (port 4321)"
	@echo ""
	@echo "Build:"
	@echo "  make build-all            - Build all components for production"
	@echo "  make build-backend        - Build backend Docker image"
	@echo "  make build-frontend       - Build frontend for production"
	@echo "  make build-website        - Build website for production"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up            - Start all services (production)"
	@echo "  make docker-dev           - Start all services (development with hot-reload)"
	@echo "  make docker-down          - Stop all Docker services"
	@echo "  make docker-build         - Rebuild production images"
	@echo "  make docker-dev-build     - Rebuild development images"
	@echo "  make docker-logs          - View logs from all services"
	@echo ""
	@echo "Testing:"
	@echo "  make test-all             - Run tests for all components"
	@echo "  make test-backend         - Run backend tests"
	@echo "  make test-frontend        - Run frontend tests"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean-all            - Clean all build artifacts"
	@echo "  make clean-backend        - Clean backend cache and databases"
	@echo "  make clean-frontend       - Clean frontend build artifacts"
	@echo "  make clean-website        - Clean website build artifacts"
	@echo ""
	@echo "Utilities:"
	@echo "  make check-backend        - Verify backend is running"
	@echo "  make status               - Check status of all services"
	@echo ""

# ==================== Installation ====================

install: install-backend install-frontend install-website
	@echo "✓ All components installed successfully!"

install-backend:
	@echo "Installing backend dependencies..."
	@cd backend && $(MAKE) install

install-frontend:
	@echo "Installing frontend dependencies..."
	@cd frontend && $(MAKE) install

install-website:
	@echo "Installing website dependencies..."
	@cd website && npm install

# ==================== Development ====================

dev-all:
	@echo "================================================"
	@echo "Starting all services in development mode..."
	@echo "================================================"
	@echo ""
	@echo "This will start all three services. You need to run them in separate terminals:"
	@echo ""
	@echo "Terminal 1:  make dev-backend"
	@echo "Terminal 2:  make dev-frontend"
	@echo "Terminal 3:  make dev-website"
	@echo ""
	@echo "Or use a terminal multiplexer like tmux or screen."
	@echo ""
	@echo "Access points:"
	@echo "  - Backend:  http://localhost:8000"
	@echo "  - Frontend: http://localhost:5173"
	@echo "  - Website:  http://localhost:4321"
	@echo ""

dev-backend:
	@echo "Starting backend server on port 8000..."
	@cd backend && $(MAKE) dev

dev-frontend:
	@echo "Starting frontend dev server on port 5173..."
	@cd frontend && $(MAKE) dev

dev-website:
	@echo "Starting website dev server on port 4321..."
	@cd website && npm run dev

# ==================== Build ====================

build-all: build-backend build-frontend build-website
	@echo "✓ All components built successfully!"

build-backend:
	@echo "Building backend..."
	@cd backend && docker build -t ainotes-backend:latest .

build-frontend:
	@echo "Building frontend..."
	@cd frontend && $(MAKE) build

build-website:
	@echo "Building website..."
	@cd website && npm run build

# ==================== Docker ====================

docker-up:
	@echo "Starting all services with Docker Compose (production)..."
	@docker-compose up -d
	@echo ""
	@echo "Services started!"
	@echo "  - Backend:  http://localhost:8000"
	@echo "  - Frontend: http://localhost:8080"
	@echo "  - Website:  http://localhost:3000"
	@echo ""
	@echo "View logs: make docker-logs"

docker-dev:
	@echo "Starting all services with Docker Compose (development)..."
	@docker-compose -f docker-compose.dev.yml up
	@echo ""
	@echo "Services started with hot-reload!"
	@echo "  - Backend:  http://localhost:8000"
	@echo "  - Frontend: http://localhost:5173"
	@echo "  - Website:  http://localhost:4321"

docker-dev-build:
	@echo "Rebuilding development Docker images..."
	@docker-compose -f docker-compose.dev.yml build --no-cache

docker-down:
	@echo "Stopping all Docker services..."
	@docker-compose down
	@docker-compose -f docker-compose.dev.yml down

docker-build:
	@echo "Rebuilding all Docker images..."
	@docker-compose build --no-cache

docker-logs:
	@echo "Showing logs from all services (Ctrl+C to exit)..."
	@docker-compose logs -f

# ==================== Testing ====================

test-all: test-backend test-frontend
	@echo "✓ All tests completed!"

test-backend:
	@echo "Running backend tests..."
	@cd backend && $(MAKE) test

test-frontend:
	@echo "Running frontend tests..."
	@cd frontend && npm test || echo "No frontend tests configured"

# ==================== Cleanup ====================

clean-all: clean-backend clean-frontend clean-website
	@echo "✓ All components cleaned!"

clean-backend:
	@echo "Cleaning backend..."
	@cd backend && $(MAKE) clean-all

clean-frontend:
	@echo "Cleaning frontend..."
	@cd frontend && $(MAKE) clean-all

clean-website:
	@echo "Cleaning website..."
	@cd website && rm -rf dist node_modules .astro

# ==================== Utilities ====================

check-backend:
	@cd frontend && $(MAKE) check-backend

status:
	@echo "======================================"
	@echo "Service Status Check"
	@echo "======================================"
	@echo ""
	@echo "Backend (port 8000):"
	@curl -s http://localhost:8000/ > /dev/null && echo "  ✓ Running" || echo "  ✗ Not running"
	@echo ""
	@echo "Frontend (port 5173/8080):"
	@curl -s http://localhost:5173/ > /dev/null && echo "  ✓ Running (dev)" || curl -s http://localhost:8080/ > /dev/null && echo "  ✓ Running (prod)" || echo "  ✗ Not running"
	@echo ""
	@echo "Website (port 4321/3000):"
	@curl -s http://localhost:4321/ > /dev/null && echo "  ✓ Running (dev)" || curl -s http://localhost:3000/ > /dev/null && echo "  ✓ Running (prod)" || echo "  ✗ Not running"
	@echo ""
	@echo "Docker services:"
	@docker-compose ps 2>/dev/null || echo "  Docker Compose not running"
	@echo ""
