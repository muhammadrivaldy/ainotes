# AI Notes

A modern web-based "Second Brain" application built with React and Vite. AI Notes is a personal knowledge base system designed to function as a conversational AI interface where users can store and retrieve information naturally through a continuous "Life Stream" timeline.

## Features

- **Chat-based Interface** - Conversational UI similar to ChatGPT/Gemini
- **Markdown Support** - Full GitHub Flavored Markdown with syntax highlighting
- **Life Stream Model** - Infinite scroll timeline instead of disjointed chat sessions
- **Auto-expanding Input** - Smart textarea that grows from 1 to 48 lines
- **Theme Toggle** - Light/Dark mode with LocalStorage persistence
- **Collapsible Sidebar** - Clean navigation with smooth transitions
- **Auto-scroll** - Automatically scrolls to latest messages
- **Responsive Design** - Works seamlessly on mobile and desktop

## Technology Stack

- **React 19.2.0** - Latest React with improved performance
- **Vite 7.2.4** - Ultra-fast build tool with Hot Module Replacement
- **Tailwind CSS 4.1.18** - Utility-first CSS framework
- **React Markdown** - Markdown rendering with GFM support
- **Lucide React** - Modern icon library (300+ icons)
- **ESLint & Prettier** - Code quality and formatting

## Quick Start

### Without Docker

#### Prerequisites

- Node.js 20 or higher
- npm or yarn

#### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# The application will be available at http://localhost:5173
```

#### Available Scripts

```bash
npm run dev      # Start development server with HMR
npm run build    # Build for production
npm run preview  # Preview production build locally
npm run lint     # Run ESLint checks
```

### With Docker

#### Docker Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

#### Production Mode

Run the optimized production build with Nginx:

```bash
# Build and start the container
docker-compose up -d

# The application will be available at http://localhost:8080
```

#### Development Mode

Run with hot-reload for active development:

```bash
# Build and start the development container
docker-compose -f docker-compose.dev.yml up -d

# The application will be available at http://localhost:5173
```

## Project Structure

```js
ainotes/
├── src/
│   ├── components/
│   │   ├── chat/              # Chat components
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── InputArea.jsx
│   │   │   └── StreamFeed.jsx
│   │   └── layout/            # Layout components
│   │       ├── AppLayout.jsx
│   │       └── Sidebar.jsx
│   ├── context/
│   │   └── ThemeContext.jsx   # Theme management
│   ├── App.jsx                # Main component
│   ├── main.jsx               # React DOM entry point
│   └── index.css              # Tailwind CSS imports
├── public/                    # Static assets
├── docker-compose.yml         # Production Docker config
├── docker-compose.dev.yml     # Development Docker config
├── Dockerfile                 # Multi-stage Docker build
├── nginx.conf                 # Nginx configuration
├── vite.config.js             # Vite configuration
└── package.json               # Dependencies and scripts
```

## Docker Commands

### Production

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up -d --build
```

### Development

```bash
# Start development server
docker-compose -f docker-compose.dev.yml up -d

# Stop development server
docker-compose -f docker-compose.dev.yml down

# View development logs
docker-compose -f docker-compose.dev.yml logs -f

# Rebuild and restart
docker-compose -f docker-compose.dev.yml up -d --build
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

## Configuration

### Customize Ports

**Production (docker-compose.yml):**

```yaml
ports:
  - "3000:80"  # Change 3000 to your desired port
```

**Development (docker-compose.dev.yml):**

```yaml
ports:
  - "3000:5173"  # Change 3000 to your desired port
```

### Environment Variables

Add environment variables in docker-compose files:

```yaml
environment:
  - VITE_API_URL=https://api.example.com
  - VITE_APP_NAME=AI Notes
```

## Docker Details

### Production Setup

- Multi-stage build for optimized image size (~25MB)
- Nginx web server for serving static files
- Gzip compression enabled
- Security headers configured
- Static asset caching (1 year for immutable assets)
- SPA routing support
- Health checks included

### Development Setup

- Hot Module Replacement (HMR) enabled
- Volume mounting for live code updates
- Node modules isolated in container
- Full React dev tools support

## Troubleshooting

### Port Already in Use

Change the port mapping in the respective docker-compose file.

### Changes Not Reflecting (Docker Development)

```bash
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d --build
```

### Container Won't Start

Check the logs:

```bash
docker-compose logs -f
```

### Node Modules Issues (Local Development)

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## React & Vite

This project uses [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) for Fast Refresh.

### React Compiler

The React Compiler is not enabled due to its impact on dev & build performance. To add it, see [React Compiler documentation](https://react.dev/learn/react-compiler/installation).

### TypeScript

For production applications, consider migrating to TypeScript with type-aware lint rules. See the [Vite TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for more information.

## License

MIT
