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
- **Smart Help System** - Automatically detects confused users and provides comprehensive guidance with examples
- **Natural Language Storage** - Save information through conversational statements
- **Document Upload** - Upload PDF files that get indexed into the knowledge base
- **Source Citations** - Responses from documents include filename and page number citations
- **Cross-Source Synthesis** - Combines insights from chat memories and uploaded documents
- **Semantic Search** - Query stored knowledge with intelligent similarity matching
- **Memory Deletion** - Remove specific memories by describing the content
- **Vector Embeddings** - Uses OpenAI embeddings for accurate semantic understanding
- **Persistent Storage** - ChromaDB for vector storage and SQLite for chat history
- **Rate Limiting** - Built-in API rate limiting (5 requests/minute)
- **CORS Support** - Pre-configured for frontend integration
- **LangGraph Agent** - Intelligent tool selection and routing with 8 specialized tools
- **Security Guards** - Prompt injection protection
- **Backward Compatible Migration** - Existing notes automatically migrate to the new schema

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

## Knowledge Sources

The knowledge base supports two types of information sources:

- **Chat Memories** (`source_type: "chat"`) — Information the user tells the assistant to remember. Stored with tags, attributed to the user, and returned without citations.
- **Documents** (`source_type: "document"`) — Uploaded PDF files that are extracted page-by-page, chunked at paragraph boundaries (~1000 chars), and stored with source filename and page number. When retrieved, responses include `[Source: filename.pdf, Page X]` citations.

Both source types share the same ChromaDB collection and are queried together via semantic search, enabling cross-source synthesis.

### Upload Flow

1. User uploads a PDF via `POST /documents/upload`
2. File is saved to `database/uploads/{user_id}/` with a timestamp prefix
3. `PyPDFLoader` extracts text page-by-page
4. Each page is split into ~1000 char chunks at paragraph boundaries
5. Document-level tags are auto-generated from filename and first-page content
6. All chunks are stored with full attribution metadata

### Migration

Existing notes without `source_type` metadata can be migrated via `POST /knowledge/migrate`. This is idempotent and safe to run multiple times.

## Smart Help System

The AI automatically detects when users are confused and provides comprehensive help with examples. This feature enhances user experience by proactively guiding users who may not understand the system's capabilities.

### How It Works

1. **Automatic Detection**: The LLM analyzes each user message for confusion signals:
   - Help requests: "what can you do?", "help", "how does this work?"
   - Confusion indicators: "I don't understand", "confused", unclear intents
   - Vague questions: "how do I start?", "what now?"

2. **Context-Aware Response**: Help content adapts based on user state:
   - **New users** (no data saved): Focus on getting started with concrete examples
   - **Existing users** (has data): Emphasize advanced features like search and tag management

3. **Tool-Based Implementation**: Uses dedicated `provide_help` tool integrated into LangGraph workflow
   - Triggered automatically by system prompt when confusion detected
   - Provides 7 capability categories with real-world examples
   - Includes pro tips and encouragement to try features

### Help Content Structure

The help response includes:
- Brief introduction to the Knowledge Assistant concept
- 8 core capabilities with concrete examples:
  1. Save information (with auto-tagging)
  2. Retrieve specific information (semantic search across all sources)
  3. Upload documents (PDF indexing and knowledge extraction)
  4. Search by meaning (context understanding across chat + documents)
  5. Manage tags (auto-cleanup)
  6. Filter by tag (category filtering)
  7. Delete information (removal by description)
  8. See everything (grouped overview by source type)
- Pro tips about privacy, auto-tagging, source citations, and semantic search
- Call-to-action encouraging user engagement

### Logging

Confusion detection events are logged for monitoring:
```python
logger.info(f"Help provided to user {user_id} - confusion detected")
```

Monitor these logs to track help usage patterns and refine detection accuracy.

### Customization

To adjust confusion detection sensitivity, modify the system prompt in `brain.py`:
```python
SYSTEM_PROMPT = """\
CONFUSION DETECTION:
# Add or remove confusion signals here
# Adjust detection criteria
"""
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
| `/tags` | GET | Yes | Get all tags with counts |
| `/tags/{tag}/items` | GET | Yes | Get items by tag |
| `/tags/regenerate` | POST | Yes | Regenerate missing tags |
| `/documents/upload` | POST | Yes | Upload PDF for knowledge indexing |
| `/knowledge/migrate` | POST | Yes | Migrate legacy metadata (idempotent) |

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3). See the [LICENSE](LICENSE) file for details.
