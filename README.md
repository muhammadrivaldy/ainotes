# AI Notes

A modern web-based "Second Brain" application built with React and Vite. AI Notes is a personal knowledge base system designed to function as a conversational AI interface where users can store and retrieve information naturally through a continuous "Life Stream" timeline.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
  - [Without Docker](#without-docker)
  - [With Docker](#with-docker)
- [Project Structure](#project-structure)
- [Google OAuth Setup](#google-oauth-setup)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
- [License](#license)

## Features

- **Google OAuth Authentication** - Secure sign-in with Google accounts
- **Chat-based Interface** - Conversational UI similar to ChatGPT/Gemini
- **Typewriter Effect** - AI messages appear character-by-character with animated cursor
- **Markdown Support** - Full GitHub Flavored Markdown with syntax highlighting
- **Life Stream Model** - Infinite scroll timeline instead of disjointed chat sessions
- **Auto-expanding Input** - Smart textarea that grows from 1 to 48 lines
- **Theme Toggle** - Light/Dark mode with LocalStorage persistence
- **Collapsible Sidebar** - Clean navigation with smooth transitions
- **User Profile** - Display user information with profile picture
- **Protected Routes** - Secure chat page with authentication guard
- **Auto-scroll** - Automatically scrolls to latest messages
- **Responsive Design** - Works seamlessly on mobile and desktop

## Technology Stack

- **React 19.2.0** - Latest React with improved performance
- **React Router DOM** - Client-side routing and navigation
- **Google OAuth** - @react-oauth/google for authentication
- **Vite 7.2.4** - Ultra-fast build tool with Hot Module Replacement
- **Tailwind CSS 4.1.18** - Utility-first CSS framework
- **React Markdown** - Markdown rendering with GFM support
- **Lucide React** - Modern icon library (300+ icons)
- **ESLint & Prettier** - Code quality and formatting

## Quick Start

> **Note:** This repository contains only the frontend code for AI Notes. You must run the backend server separately for full functionality.  
> The backend source code and setup instructions are available at: [https://github.com/muhammadrivaldy/ainotes-backend](https://github.com/muhammadrivaldy/ainotes-backend)

### Without Docker

#### Prerequisites

- Node.js 20 or higher
- npm or yarn

#### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.development

# Add your Google OAuth Client ID to .env.development
# See "Google OAuth Setup" section below

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
│   │   ├── auth/              # Authentication components
│   │   │   └── ProtectedRoute.jsx
│   │   ├── chat/              # Chat components
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── InputArea.jsx
│   │   │   └── StreamFeed.jsx
│   │   └── layout/            # Layout components
│   │       ├── AppLayout.jsx
│   │       └── Sidebar.jsx
│   ├── context/
│   │   ├── AuthContext.jsx    # Authentication management
│   │   └── ThemeContext.jsx   # Theme management
│   ├── hooks/
│   │   └── useTypewriter.js   # Typewriter effect hook
│   ├── pages/
│   │   ├── ChatPage.jsx       # Main chat interface
│   │   └── LoginPage.jsx      # Google OAuth login
│   ├── services/
│   │   └── api.js             # API service layer
│   ├── App.jsx                # Route configuration
│   ├── main.jsx               # React DOM entry point
│   └── index.css              # Tailwind CSS imports
├── public/                    # Static assets
├── .env.example               # Environment variables template
├── .env.development           # Development environment variables
├── docker-compose.yml         # Production Docker config
├── docker-compose.dev.yml     # Development Docker config
├── Dockerfile                 # Multi-stage Docker build
├── nginx.conf                 # Nginx configuration
├── vite.config.js             # Vite configuration
└── package.json               # Dependencies and scripts
```

## Google OAuth Setup

To enable Google authentication, you need to create OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" → "Credentials"
4. Click "Create Credentials" → "OAuth client ID"
5. Select "Web application" as the application type
6. Add authorized JavaScript origins:
   - `http://localhost:5173` (for local development)
   - Your production domain (when deploying)
7. Copy the Client ID
8. Add it to `.env.development`:

   ```bash
   VITE_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   ```

**Note:** The OAuth consent screen must be configured before creating credentials.

## Configuration

### Environment Variables

Add environment variables in docker-compose files:

```yaml
environment:
  - VITE_API_URL=https://api.example.com
  - VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
  - VITE_APP_NAME=AI Notes
```

Available environment variables:

- `VITE_API_URL` - Backend API endpoint (default: `http://localhost:8000`)
- `VITE_GOOGLE_CLIENT_ID` - Google OAuth Client ID (required for authentication)

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3). See the [LICENSE](LICENSE) file for details.
