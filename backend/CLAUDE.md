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

### Eight Tools

1. **provide_help** - Context-aware help for confused users
2. **add_recall** - Stores chat memories with full attribution metadata
3. **add_document** - Processes uploaded PDFs into indexed knowledge chunks
4. **query_recall** - Semantic similarity search with source citations
5. **delete_recall** - Finds and deletes by similarity match
6. **get_tags** - Lists tags with auto-deduplication
7. **get_all_knowledge** - Lists all knowledge grouped by source type (chat vs documents)
8. **get_items_by_tag** - Filters knowledge by specific tag

### Metadata Schema

Each item in ChromaDB includes:
- `user_id` (int) - Data isolation key
- `tags` (string) - Comma-separated tags
- `source_type` (string) - "chat" or "document"
- `source` (string) - "user" for chat memories, filename for documents
- `source_path` (string) - Full file path for documents
- `page` (string) - Page number for document chunks
- `created_at` (string) - ISO timestamp

### Storage

- **ChromaDB** (`database/chroma/`) - Shared collection "second_brain" with per-user metadata filtering
- **SQLite** (`database/chat_history.db`) - Users and conversation history
- **Uploads** (`database/uploads/{user_id}/`) - Uploaded PDF files

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
| `/tags` | GET | Yes | Get all tags with counts |
| `/tags/{tag}/items` | GET | Yes | Get items by tag |
| `/tags/regenerate` | POST | Yes | Regenerate missing tags |
| `/documents/upload` | POST | Yes | Upload PDF for knowledge indexing |
| `/knowledge/migrate` | POST | Yes | Migrate legacy metadata (idempotent) |

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
