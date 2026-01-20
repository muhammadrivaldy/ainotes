# AI Notes API

A FastAPI-based "Second Brain" API that stores and retrieves information using vector embeddings. This backend provides intelligent memory storage and semantic search capabilities, allowing users to save, query, and delete information through natural language interactions powered by LangChain and ChromaDB.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
  - [Without Docker](#without-docker)
  - [With Docker](#with-docker)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [License](#license)

## Features

- **User Authentication** - Google OAuth integration with JWT session tokens
- **Per-User Data Isolation** - Each user has their own chat history and knowledge base
- **Natural Language Storage** - Save information through conversational statements
- **Semantic Search** - Query stored knowledge with intelligent similarity matching
- **Memory Deletion** - Remove specific memories by describing the content
- **Vector Embeddings** - Uses OpenAI embeddings for accurate semantic understanding
- **Persistent Storage** - ChromaDB for vector storage and SQLite for chat history
- **Rate Limiting** - Built-in API rate limiting (5 requests/minute)
- **CORS Support** - Pre-configured for frontend integration
- **LangGraph Agent** - Intelligent tool selection and routing
- **Security Guards** - Prompt injection protection

## Technology Stack

- **FastAPI** - Modern, high-performance web framework
- **LangChain** - LLM orchestration and tool management
- **LangGraph** - Agent workflow and state management
- **ChromaDB** - Vector database for embeddings
- **SQLModel** - SQL database ORM (SQLite)
- **OpenRouter** - LLM API provider (GPT-4o-mini)
- **python-jose** - JWT token handling
- **Uvicorn** - ASGI server
- **SlowAPI** - Rate limiting middleware

## Quick Start

### Without Docker

#### Prerequisites

- Python 3.11 or higher
- pip or poetry
- OpenRouter API key

#### Installation

```bash
# Install dependencies using Makefile (recommended)
make install

# Or manually
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY and JWT_SECRET_KEY

# Run the server
make dev

# The API will be available at http://localhost:8000
```

#### Available Commands

```bash
make install    # Create venv and install dependencies
make dev        # Start server with auto-reload
make run        # Start server (production mode)
make clean      # Remove Python cache files
make clean-db   # Remove database files
make clean-all  # Remove everything including venv
make help       # Show all available commands
```

### With Docker

#### Docker Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- OpenRouter API key

#### Production Mode

Run the API in production mode:

```bash
# Configure environment
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY and JWT_SECRET_KEY

# Build and start the container
docker-compose up -d

# The API will be available at http://localhost:8000
```

## Project Structure

```js
ainotes/
├── database/                  # Persistent storage (git ignored)
│   ├── chat_history.db        # SQLite database with users and messages
│   └── chroma/                # ChromaDB vector embeddings
│       └── user_{id}/         # Per-user vector collections
├── brain.py                   # Second Brain agent with LangGraph
├── main.py                    # FastAPI application entry point
├── models.py                  # Pydantic/SQLModel data models
├── database.py                # SQLModel database configuration
├── auth.py                    # JWT authentication logic
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (git ignored)
├── .env.example               # Environment variables template
├── .dockerignore              # Docker build exclusions
├── Dockerfile                 # Docker build configuration
├── docker-compose.yml         # Docker Compose configuration
├── Makefile                   # Local development commands
└── README.md                  # This file
```

## Configuration

### Environment Variables

Configure the API using the `.env` file:

```env
# OpenRouter Configuration (required)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_EMBEDDING_MODEL=text-embedding-3-small
OPENROUTER_AI_MODEL=openai/gpt-4o-mini

# JWT Configuration (required)
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_EXPIRATION_DAYS=7
```

### Rate Limiting

Adjust rate limits in `main.py`:

```python
@app.post("/chat")
@limiter.limit("10/minute")  # Change from 5 to 10 requests per minute
async def chat_endpoint(...):
```

## Authentication

The API uses JWT-based authentication with Google OAuth:

1. Frontend authenticates user with Google OAuth
2. Frontend sends Google credential to `POST /auth/google`
3. Backend verifies credential and creates/retrieves user
4. Backend returns JWT token (valid for 7 days)
5. Frontend includes JWT in Authorization header for all requests

### API Endpoints

| Endpoint | Method | Auth | Description |
| ---------- | -------- | ---- | ------------- |
| `/` | GET | No | Health check |
| `/auth/google` | POST | No | Google OAuth login |
| `/auth/me` | GET | Yes | Get current user |
| `/chat` | POST | Yes | Send message (rate limited: 5/min) |
| `/history` | GET | Yes | Get user's chat history |
| `/history` | DELETE | Yes | Clear user's chat history |

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3). See the [LICENSE](LICENSE) file for details.
