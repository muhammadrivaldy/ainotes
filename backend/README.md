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
- [Architecture](#architecture)
- [License](#license)

## Features

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
# Edit .env and add your OPENROUTER_API_KEY

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
# Edit .env and add your OPENROUTER_API_KEY

# Build and start the container
docker-compose up -d

# The API will be available at http://localhost:8000
```

## Project Structure

```js
ainotes/
├── db_chroma/                 # Persistent storage
│   ├── chroma.sqlite3         # ChromaDB metadata
│   └── {collection-id}/       # Vector embeddings
├── brain.py                   # Second Brain agent with LangGraph
├── main.py                    # FastAPI application entry point
├── models.py                  # Pydantic data models
├── database.py                # SQLModel database configuration
├── chat_history.db            # SQLite chat history (persistent)
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
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Rate Limiting

Adjust rate limits in `main.py`:

```python
@app.post("/chat")
@limiter.limit("10/minute")  # Change from 5 to 10 requests per minute
async def chat_endpoint(...):
```

## Architecture

### Agent Flow

1. **User Message** → FastAPI endpoint
2. **Security Check** → Forbidden phrase filtering
3. **History Retrieval** → Load from SQLite
4. **LangGraph Agent** → Process with tools
5. **Tool Execution** → add_recall / query_recall / delete_recall
6. **Response Generation** → LLM generates reply
7. **Save to History** → Store in SQLite
8. **Return Response** → Send to user

### Tools

- **add_recall** - Stores information in vector database
- **query_recall** - Retrieves information via semantic search
- **delete_recall** - Removes information by similarity match

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3). See the [LICENSE](LICENSE) file for details.
