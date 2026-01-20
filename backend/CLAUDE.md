# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Notes API is a FastAPI-based "Second Brain" backend that stores and retrieves information using vector embeddings. It provides intelligent memory storage and semantic search through natural language interactions with per-user data isolation.

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
make clean-db          # Remove database/ folder contents
make clean-all         # Remove everything including venv
```

## Environment Setup

Requires the following in `.env` file (copy from `.env.example`):
- `OPENROUTER_API_KEY` - API key for LLM and embeddings
- `JWT_SECRET_KEY` - Secret key for JWT token signing

## Architecture

### Request Flow

```text
POST /chat → main.py → Verify JWT → Get user → Save user message to SQLite →
Load user's history → brain.py (user-specific SecondBrain) →
LangGraph agent with tools → Save AI response → Return
```

### Key Components

- **main.py** - FastAPI application with auth and chat endpoints
- **auth.py** - JWT authentication and Google OAuth token handling
- **brain.py** - `SecondBrain` class implementing user-specific LangGraph agent
- **database.py** - SQLModel/SQLite configuration with user functions
- **models.py** - Pydantic/SQLModel models for API and database

### Database Models

- **User** - Stores user info (google_id, email, name, picture)
- **ChatMessage** - Stores messages with user_id foreign key

### LangGraph Agent (brain.py)

The `SecondBrain` class is instantiated per-user and builds a LangGraph `StateGraph` with:

- **agent node** - Calls LLM with bound tools
- **tools node** - `ToolNode` executing the three tools
- **Conditional routing** - Routes to tools if `tool_calls` present, else ends

### Three Tools

1. **add_recall** - Stores text in user's ChromaDB collection
2. **query_recall** - Semantic similarity search (k=3) in user's collection
3. **delete_recall** - Finds and deletes by similarity match

### Storage

- **ChromaDB** (`database/chroma/user_{id}/`) - Per-user vector embeddings
- **SQLite** (`database/chat_history.db`) - Users and conversation history

### LLM Configuration

Uses OpenRouter API with:

- Chat: `openai/gpt-4o-mini`
- Embeddings: `text-embedding-3-small`

## API Endpoints

| Endpoint | Method | Auth | Description |
| ---------- | -------- | ---- | ------------- |
| `/` | GET | No | Health check |
| `/auth/google` | POST | No | Google OAuth login, returns JWT |
| `/auth/me` | GET | Yes | Get current user info |
| `/chat` | POST | Yes | Main chat (rate limited: 5/min) |
| `/history` | GET | Yes | Retrieve user's messages |
| `/history` | DELETE | Yes | Clear user's messages |

## Authentication Flow

1. Frontend sends Google OAuth credential to `/auth/google`
2. Backend decodes credential, creates/updates user in DB
3. Backend returns JWT token (7 days expiry)
4. Frontend includes `Authorization: Bearer <token>` in all requests
5. Backend validates JWT and extracts user for each request

## Security Features

- JWT-based authentication with configurable expiration
- Per-user data isolation (chat history and knowledge base)
- Prompt injection protection via forbidden phrases filter in `brain.py:170-176`
- Rate limiting via SlowAPI (5 req/min on `/chat`)
- Generic error responses to avoid detail leakage
