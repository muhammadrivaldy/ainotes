# AI Notes

AI-powered "Second Brain" application for storing and retrieving information through natural language conversations.

## Table of Contents

- [Structure](#structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Common Commands](#common-commands)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Structure

```text
ainotes/
├── backend/     # FastAPI + LangGraph + ChromaDB
├── frontend/    # React 19 + Vite
├── landing/     # Astro landing page
```

## Quick Start

### Development

```bash
# 1. Setup environment variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit both .env files with your API keys

# 2. Run with Docker (recommended)
docker-compose -f docker-compose.dev.yml up

# OR run locally (requires Python 3.11+ and Node.js 20+)
make install    # Install all dependencies
make dev-all    # Requires 3 terminals for backend, frontend, landing
```

**Access:**

- Backend API: <http://localhost:8000>
- Frontend: <http://localhost:5173>
- Landing: <http://localhost:4321>

### Production

```bash
docker-compose up -d
```

**Access:**

- Backend API: <http://localhost:8000>
- Frontend: <http://localhost:8080>
- Landing: <http://localhost:3000>

## Configuration

### Required API Keys

1. **OpenRouter API Key** (backend)
   - Get from: <https://openrouter.ai/>
   - Add to `backend/.env`: `OPENROUTER_API_KEY=your_key`

2. **Google OAuth Client ID** (frontend)
   - Get from: <https://console.cloud.google.com/apis/credentials>
   - Add to `frontend/.env`: `VITE_GOOGLE_CLIENT_ID=your_id`
   - Add authorized origin: `http://localhost:5173`

## Common Commands

```bash
make help          # Show all commands
make install       # Install all dependencies
make dev-all       # Start dev servers (3 terminals needed)
make docker-up     # Start production with Docker
make docker-down   # Stop Docker services
make clean-all     # Clean all build artifacts
make status        # Check service status
```

## Documentation

- [Backend](backend/README.md) - FastAPI, LangChain, ChromaDB
- [Frontend](frontend/README.md) - React, authentication, UI
- [Landing](landing/README.md) - Astro landing page

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to get started, coding standards, and the pull request process.

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3). See the [LICENSE](LICENSE) file for details.
