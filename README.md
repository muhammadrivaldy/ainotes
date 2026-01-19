# AI Notes - Monorepo

A modern AI-powered "Second Brain" application for storing and retrieving information through natural language conversations. This monorepo contains all components of the AI Notes project.

## Repository Structure

```
ainotes/
├── backend/        # Python FastAPI backend with LangGraph agent
├── frontend/       # React 19 web application
├── website/        # Astro landing page
├── docker-compose.yml
├── Makefile
└── README.md
```

## Components Overview

### Backend (Python/FastAPI)
- **Technology:** FastAPI, LangChain, LangGraph, ChromaDB, SQLite
- **Purpose:** AI agent backend with vector storage for semantic search
- **Port:** 8000
- **Documentation:** [backend/README.md](backend/README.md)

**Key Features:**
- Natural language storage and retrieval
- Vector embeddings with ChromaDB
- LangGraph agent with three tools (add/query/delete)
- Rate limiting and CORS support
- Google OAuth integration

### Frontend (React)
- **Technology:** React 19, Vite, Tailwind CSS, React Router
- **Purpose:** Web-based chat interface
- **Port:** 5173 (dev) / 8080 (production)
- **Documentation:** [frontend/README.md](frontend/README.md)

**Key Features:**
- Google OAuth authentication
- Chat interface with typewriter effect
- Markdown rendering with syntax highlighting
- Light/dark theme toggle
- Infinite scroll "Life Stream" timeline
- Auto-expanding textarea

### Website (Astro)
- **Technology:** Astro 5.16, Tailwind CSS, TypeScript
- **Purpose:** Marketing landing page
- **Port:** 4321 (dev) / 3000 (production)
- **Documentation:** [website/README.md](website/README.md)

**Key Features:**
- Internationalization (English/Indonesian)
- Clean, content-focused design
- Mobile-responsive
- Open source template for customization

## Quick Start

### Prerequisites

- **Backend:** Python 3.11+, OpenRouter API key
- **Frontend:** Node.js 20+
- **Website:** Node.js 18+
- **Docker:** Docker 20.10+ and Docker Compose 2.0+ (optional)

### Development (Without Docker)

1. **Setup Environment:**
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY

   # Frontend
   cd ../frontend
   cp .env.example .env.development
   # Add your VITE_GOOGLE_CLIENT_ID and VITE_API_URL
   ```

2. **Start All Services:**
   ```bash
   # From project root
   make dev-all
   ```

   Or start each component individually:
   ```bash
   # Terminal 1 - Backend
   cd backend && make dev

   # Terminal 2 - Frontend
   cd frontend && make dev

   # Terminal 3 - Website
   cd website && npm run dev
   ```

3. **Access Services:**
   - Backend API: http://localhost:8000
   - Frontend App: http://localhost:5173
   - Landing Page: http://localhost:4321

### Production (With Docker)

```bash
# Build and start all services
docker-compose up -d

# Access services
# - Backend API: http://localhost:8000
# - Frontend App: http://localhost:8080
# - Landing Page: http://localhost:3000
```

## Unified Commands (Makefile)

```bash
make install        # Install dependencies for all components
make dev-all        # Start all services in development mode
make build-all      # Build all components for production
make clean-all      # Clean all build artifacts and dependencies
make test-all       # Run tests for all components
make help           # Show all available commands
```

## Architecture

### System Flow

```
User → Website (Landing Page)
       ↓
User → Frontend (React App) ← → Backend (FastAPI)
                                   ↓
                              ChromaDB (Vectors)
                              SQLite (History)
```

### Communication

- Frontend communicates with Backend via REST API
- Backend uses OpenRouter for LLM inference
- ChromaDB stores vector embeddings for semantic search
- SQLite stores chat history

### Docker Network

All services run on the `ainotes-network` bridge network:
- Service names: `ainotes-api`, `ainotes-frontend`, `ainotes-website`
- Inter-service communication uses service names as hostnames

## Configuration

### Backend (.env)
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Frontend (.env.development)
```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID
3. Add authorized JavaScript origins:
   - `http://localhost:5173` (development)
   - Your production domain
4. Copy Client ID to frontend `.env.development`

## Data Persistence

The following data is persisted across container restarts:

- `backend/db_chroma/` - Vector embeddings (ChromaDB)
- `backend/chat_history.db` - Conversation history (SQLite)

## Troubleshooting

### Port Conflicts
If ports are already in use, modify `docker-compose.yml` or use different ports when running locally.

### Backend Connection Issues
Ensure the backend is running before starting the frontend:
```bash
curl http://localhost:8000/
```

### Google OAuth Issues
Verify that:
1. OAuth Client ID is correctly set in frontend `.env.development`
2. The current URL is added to authorized JavaScript origins
3. OAuth consent screen is configured

### Database Issues
```bash
# Clean databases
cd backend && make clean-db

# Or with Docker
docker-compose down -v
docker-compose up -d
```

## Development Guidelines

### Adding Features
1. Backend changes: See `backend/CLAUDE.md`
2. Frontend changes: See `frontend/CLAUDE.md`
3. Website changes: See `website/CLAUDE.md`

### Code Quality
```bash
# Backend
cd backend && make lint && make format

# Frontend
cd frontend && make lint && make format
```

### Testing
```bash
# Backend
cd backend && make test

# Frontend
cd frontend && npm test
```

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3).

- Backend: [backend/LICENSE](backend/LICENSE)
- Frontend: [frontend/LICENSE](frontend/LICENSE)
- Website: [website/LICENSE](website/LICENSE)

You are free to fork, modify, and self-host this application. See the LICENSE files for complete terms.

## Git History

This monorepo was created by merging three separate repositories while preserving complete git history:

- **ainotes-backend** - 6 commits
- **ainotes-frontend** - 21 commits
- **ainotes-landpage** - 7 commits

**Total preserved commits:** 34 commits from the original repositories.

## Repository Information

- **Original Repositories:**
  - Backend: `git@github.com:muhammadrivaldy/ainotes-backend.git`
  - Frontend: `git@github.com:muhammadrivaldy/ainotes-frontend.git`
  - Landing Page: `git@github.com:muhammadrivaldy/ainotes-landpage.git`

- **Author:** muhammadrivaldy16@gmail.com

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

For detailed documentation on each component, see the respective README files:
- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
- [Website Documentation](website/README.md)
