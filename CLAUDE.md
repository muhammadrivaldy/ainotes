# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Notes API is a FastAPI-based "Second Brain" backend that stores and retrieves information using vector embeddings. It provides intelligent memory storage and semantic search through natural language interactions.

## Common Commands

```bash
# Setup
make install           # Create venv and install dependencies

# Development
make dev               # Start server with auto-reload (port 8000)
make run               # Start server in production mode

# Code quality
make lint              # Check code style with flake8
make format            # Format code with black
make test              # Run pytest tests (tests/ directory)

# Cleanup
make clean-db          # Remove chat_history.db and db_chroma/
make clean-all         # Remove everything including venv
```

## Environment Setup

Requires `OPENROUTER_API_KEY` in `.env` file. Copy from `.env.example`.

## Architecture

### Request Flow

```text
POST /chat → main.py → Save user message to SQLite → Load history →
brain.py (SecondBrain) → LangGraph agent with tools → Save AI response → Return
```

### Key Components

- **main.py** - FastAPI application with endpoints (`/`, `/chat`, `/history`)
- **brain.py** - `SecondBrain` class implementing LangGraph agent with three tools
- **database.py** - SQLModel/SQLite configuration for chat history
- **models.py** - Pydantic models for API requests/responses

### LangGraph Agent (brain.py)

The `SecondBrain` class builds a LangGraph `StateGraph` with:

- **agent node** - Calls LLM with bound tools
- **tools node** - `ToolNode` executing the three tools
- **Conditional routing** - Routes to tools if `tool_calls` present, else ends

### Three Tools

1. **add_recall** - Stores text in ChromaDB vector store
2. **query_recall** - Semantic similarity search (k=3) in ChromaDB
3. **delete_recall** - Finds and deletes by similarity match

### Storage

- **ChromaDB** (`db_chroma/`) - Vector embeddings for semantic memory
- **SQLite** (`chat_history.db`) - Conversation history persistence

### LLM Configuration

Uses OpenRouter API with:

- Chat: `openai/gpt-4o-mini`
- Embeddings: `text-embedding-3-small`

## API Endpoints

| Endpoint | Method | Description |
| ---------- | -------- | ------------- |
| `/` | GET | Health check |
| `/chat` | POST | Main chat (rate limited: 5/min) |
| `/history` | GET | Retrieve all messages |
| `/history` | DELETE | Clear all messages |

## Security Features

- Prompt injection protection via forbidden phrases filter in `brain.py:176-181`
- Rate limiting via SlowAPI (5 req/min on `/chat`)
- Generic error responses to avoid detail leakage
