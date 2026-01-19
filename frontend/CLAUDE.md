# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Notes is a React 19 frontend application for an AI-powered chat interface. It requires a separate backend server [ainotes-backend](https://github.com/muhammadrivaldy/ainotes-backend) running on `http://localhost:8000`.

## Common Commands

```bash
# Development
make dev          # Start Vite dev server on http://localhost:5173
make install      # Install npm dependencies
make start        # Install + run dev server

# Code Quality
make lint         # Run ESLint
make format       # Format code with Prettier

# Build
make build        # Production build
make preview      # Preview production build

# Utilities
make check-backend  # Verify backend is running on port 8000
make clean          # Remove build artifacts
```

## Architecture

**Stack:** React 19 + Vite + Tailwind CSS + React Router DOM

**State Management:**

- `AuthContext` - User authentication state (Google OAuth, persisted in localStorage)
- `ThemeContext` - Dark/light theme toggle (persisted in localStorage)
- Local state in ChatPage for messages and streaming

**Key Directories:**

- `src/components/` - UI components organized by feature (auth, chat, layout)
- `src/context/` - React Context providers (Auth, Theme)
- `src/hooks/` - Custom hooks (useTypewriter for streaming animation)
- `src/pages/` - Route-level components (ChatPage, LoginPage)
- `src/services/api.js` - Backend API layer (chat, history, health endpoints)

**Route Structure:**

- `/login` - Public login page with Google OAuth
- `/` - Protected ChatPage wrapped in ProtectedRoute

**Component Hierarchy:**

```text
App → Routes
  ├── LoginPage
  └── ProtectedRoute → ChatPage → AppLayout
                                    ├── Sidebar
                                    ├── StreamFeed → MessageBubble
                                    └── InputArea
```

## Code Patterns

**Markdown Rendering:** Uses `react-markdown` with `remark-gfm` and `remark-breaks` plugins for GitHub Flavored Markdown support.

**Typewriter Effect:** The `useTypewriter` hook animates AI responses character-by-character (20ms default interval).

**Auto-expanding Textarea:** InputArea auto-resizes from 1 to 48 lines based on content.

**Input Handling:** Enter submits, Shift+Enter creates newline.

## Configuration

- **Environment:** Copy `.env.example` to `.env` and set `VITE_GOOGLE_CLIENT_ID` and `VITE_API_URL`
- **ESLint:** Flat config in `eslint.config.js` with React Hooks rules
- **Prettier:** Configured with Tailwind class sorting plugin
