# AI Notes API

A FastAPI-based "Second Brain" API that stores and retrieves information using vector embeddings. This backend provides intelligent memory storage and semantic search capabilities, allowing users to save, query, and delete information through natural language interactions powered by LangChain and ChromaDB.

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

> **Note:** This repository provides the backend API for the AI Notes application.  
> To use this API with a web interface, connect it to the [ainotes-frontend](https://github.com/muhammadrivaldy/ainotes-frontend) project.

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

## Docker Commands

### Production

```bash
# Start the API
docker-compose up -d

# Stop the API
docker-compose down

# View logs
docker-compose logs -f

# Restart the API
docker-compose restart

# Rebuild and restart
docker-compose up -d --build
```

### Clean Up

```bash
# Remove containers and networks
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Remove everything including images
docker-compose down -v --rmi all
```

## API Endpoints

### Chat

**POST** `/chat`

Send a message to the Second Brain assistant.

**Request:**

```json
{
  "message": "Remember that my favorite color is blue"
}
```

**Response:**

```json
{
  "response": "Information stored successfully."
}
```

### History

**GET** `/history`

Retrieve all chat history.

**Response:**

```json
[
  {
    "id": 1,
    "role": "user",
    "content": "Remember that my favorite color is blue",
    "timestamp": "2026-01-17T10:30:00"
  },
  {
    "id": 2,
    "role": "assistant",
    "content": "Information stored successfully.",
    "timestamp": "2026-01-17T10:30:01"
  }
]
```

**DELETE** `/history`

Clear all chat history.

**Response:**

```json
{
  "status": "History cleared"
}
```

### Health Check

**GET** `/`

Check API status.

**Response:**

```json
{
  "status": "Second Brain is active"
}
```

## Usage Examples

### Store Information

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Remember that my favorite color is blue"}'
```

### Query Information

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my favorite color?"}'
```

### Delete Information

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Delete information about my favorite color"}'
```

### Get Chat History

```bash
curl http://localhost:8000/history
```

### Clear History

```bash
curl -X DELETE http://localhost:8000/history
```

## Connecting with Frontend

This API is designed to work with the AI Notes frontend application.

### Docker Network Setup

The API runs on a Docker network called `ainotes-network`. The frontend container should join the same network to communicate with the API.

**Frontend docker-compose.yml configuration:**

```yaml
version: '3.8'

services:
  frontend:
    # ... your frontend config ...
    networks:
      - ainotes-network

networks:
  ainotes-network:
    name: ainotes-network
    driver: bridge
```

### API Access

- **From host machine:** `http://localhost:8000`
- **From frontend container:** `http://ainotes-api:8000`

The frontend should use the service name `ainotes-api` as the hostname when making API requests from within Docker.

**Frontend environment variable:**

```env
VITE_API_URL=http://ainotes-api:8000
```

### Starting Both Services

```bash
# Start backend
cd /path/to/ainotes-api
docker-compose up -d

# Start frontend
cd /path/to/ainotes-frontend
docker-compose up -d
```

Both containers will communicate through the `ainotes-network` bridge network.

## Configuration

### Environment Variables

Configure the API using the `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Customize Port

Edit `docker-compose.yml`:

```yaml
ports:
  - "3000:8000"  # Change 3000 to your desired port
```

Or for local development, modify `main.py`:

```python
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
```

### Rate Limiting

Adjust rate limits in `main.py`:

```python
@app.post("/chat")
@limiter.limit("10/minute")  # Change from 5 to 10 requests per minute
async def chat_endpoint(...):
```

### CORS Configuration

Modify allowed origins in `main.py`:

```python
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://yourdomain.com",  # Add your domain
]
```

## Docker Details

### Production Setup

- Python 3.11 slim base image
- Optimized for production workloads
- Persistent volumes for data storage
- Health checks included
- Auto-restart on failure
- Minimal attack surface

### Data Persistence

The Docker setup persists:

- `db_chroma/` - Vector embeddings storage (ChromaDB)
- `chat_history.db` - SQLite database for chat history

These are mounted as volumes and survive container restarts.

## Troubleshooting

### Port Already in Use

Change the port mapping in `docker-compose.yml` or use a different port when running locally.

### OpenRouter API Key Issues

Ensure your `.env` file has a valid `OPENROUTER_API_KEY`:

```bash
# Check if .env exists
cat .env

# Should show:
OPENROUTER_API_KEY=sk-or-v1-...
```

### Database Locked Error

If SQLite shows database locked error:

```bash
# Stop the container
docker-compose down

# Remove the database file
rm chat_history.db

# Restart
docker-compose up -d
```

### ChromaDB Collection Issues

If vector store has issues:

```bash
# Using Makefile
make clean-db

# Or manually remove ChromaDB
rm -rf db_chroma/
```

### Container Won't Start

Check the logs:

```bash
docker-compose logs -f
```

### Changes Not Reflecting (Local Development)

```bash
# Restart with reload
make dev

# Or force rebuild with Docker
docker-compose down
docker-compose up -d --build
```

### Dependencies Issues

```bash
# Clear and reinstall
make clean-all
make install

# Or with Docker, rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
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
