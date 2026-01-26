# Makefile for AI Notes Landing Page

# Variables
NPM := npm
DOCKER := docker
DOCKER_COMPOSE := docker-compose
APP_NAME := ainotes-landing
PORT := 4321

.PHONY: all help install dev build preview clean docker-build docker-run

# Default target
all: help

# Help command
help:
	@echo "AI Notes Landing Page Makefile"
	@echo "------------------------------"
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Start development server"
	@echo "  make build         - Build for production"
	@echo "  make preview       - Preview production build"
	@echo "  make clean         - Remove build artifacts and dependencies"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"

# Installation
install:
	$(NPM) install

# Development
dev:
	$(NPM) run dev

# Build
build:
	$(NPM) run build

# Preview
preview:
	$(NPM) run preview

# Clean
clean:
	rm -rf dist node_modules .astro

# Docker
docker-build:
	$(DOCKER) build -t $(APP_NAME) .

docker-run:
	$(DOCKER) run -p $(PORT):$(PORT) $(APP_NAME)
