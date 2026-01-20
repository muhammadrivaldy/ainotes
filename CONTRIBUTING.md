# Contributing to AI Notes

Thank you for your interest in contributing to AI Notes! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)
- [Community Guidelines](#community-guidelines)

## Ways to Contribute

There are many ways to contribute to AI Notes:

- **Code contributions**: Bug fixes, new features, performance improvements
- **Documentation**: Improve README files, add code comments, create tutorials
- **Bug reports**: Report issues you encounter
- **Feature requests**: Suggest new features or improvements
- **Testing**: Test the application and report issues
- **Design**: Improve UI/UX, create mockups

## Getting Started

### Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.11+
- **Docker** (optional, but recommended for development)
- **Git** for version control

### Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/ainotes.git
   cd ainotes
   ```

2. **Set up environment variables**

   ```bash
   # Copy example env files
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Get required API keys**
   - **OpenRouter API Key**: Get from [OpenRouter](https://openrouter.ai/) and add to `backend/.env`
   - **Google OAuth Client ID**: Get from [Google Cloud Console](https://console.cloud.google.com/apis/credentials) and add to `frontend/.env`
     - Add `http://localhost:5173` as an authorized origin

4. **Install dependencies and run**

   **Option A: Docker (Recommended)**

   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

   **Option B: Local development**

   ```bash
   make install    # Install all dependencies
   make dev-all    # Start all dev servers (requires 3 terminals)
   ```

5. **Access the application**
   - Backend API: <http://localhost:8000>
   - Frontend: <http://localhost:5173>
   - Landing page: <http://localhost:4321>

## Project Structure

```text
ainotes/
├── backend/       # FastAPI + LangGraph + ChromaDB
│   ├── main.py           # API server entry point
│   ├── brain.py          # LangGraph agent logic
│   ├── auth.py           # Authentication
│   ├── models.py         # Database models
│   ├── database.py       # Database setup
│   └── requirements.txt  # Python dependencies
├── frontend/      # React 19 + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/        # Page components
│   │   ├── context/      # React Context providers
│   │   ├── hooks/        # Custom React hooks
│   │   └── services/     # API services
│   └── package.json
└── landing/       # Astro landing page
    ├── src/
    │   ├── components/   # Astro components
    │   ├── lib/          # Utilities & translations
    │   └── pages/        # Page routes
    └── package.json
```

Each directory has its own `CLAUDE.md` and `README.md` with detailed documentation.

## Development Workflow

1. **Create a new branch** for your feature or bug fix

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow the existing code style
   - Add comments where necessary
   - Test your changes thoroughly

3. **Test your changes**

   ```bash
   # Backend tests (if available)
   cd backend
   make test

   # Frontend linting
   cd frontend
   make lint
   ```

4. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `style:` for formatting changes
   - `refactor:` for code refactoring
   - `test:` for adding tests
   - `chore:` for maintenance tasks

## Coding Standards

### General Guidelines

- Write clear, self-documenting code
- Keep functions small and focused
- Use meaningful variable and function names
- Avoid deep nesting
- Handle errors appropriately
- Don't commit commented-out code or console.logs

### Backend (Python)

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints where appropriate
- Document functions with docstrings
- Use async/await for I/O operations
- Keep routes in `main.py` clean and delegate logic to separate modules

### Frontend (React)

- Use functional components with hooks
- Follow existing component structure
- Use meaningful component and prop names
- Keep components focused and reusable
- Use Tailwind CSS for styling (avoid inline styles)
- Run `make lint` and `make format` before committing

### Landing (Astro)

- Follow existing component patterns
- Use `data-i18n` attributes for translatable content
- Add translations to `src/lib/translations.ts`
- Use Tailwind CSS utility classes

## Submitting Changes

### Pull Request Process

1. **Push your branch to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Go to the [AI Notes repository](https://github.com/muhammadrivaldy/ainotes)
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template with:
     - Clear description of changes
     - Related issue numbers (if applicable)
     - Screenshots (for UI changes)
     - Testing performed

3. **Wait for review**
   - Maintainers will review your PR
   - Address any feedback or requested changes
   - Once approved, your PR will be merged

### PR Guidelines

- Keep PRs focused on a single feature or bug fix
- Update documentation if needed
- Ensure all tests pass
- Keep commit history clean
- Rebase on main if needed to resolve conflicts

## Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Detailed steps to reproduce the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**:
   - OS (Linux, macOS, Windows)
   - Browser (if frontend issue)
   - Python version (if backend issue)
   - Node.js version (if frontend issue)
6. **Screenshots/logs**: If applicable
7. **Possible solution**: If you have ideas on how to fix it

Create an issue on [GitHub Issues](https://github.com/muhammadrivaldy/ainotes/issues) with the "bug" label.

## Requesting Features

When requesting features, please include:

1. **Problem statement**: What problem does this solve?
2. **Proposed solution**: How should this feature work?
3. **Alternatives considered**: Other approaches you've thought about
4. **Use cases**: Real-world scenarios where this would be useful
5. **Mockups/examples**: If applicable

Create an issue on [GitHub Issues](https://github.com/muhammadrivaldy/ainotes/issues) with the "enhancement" label.

## Community Guidelines

- **Be respectful**: Treat everyone with respect and kindness
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Remember that maintainers and contributors are often volunteers
- **Be collaborative**: Work together to make AI Notes better
- **Ask questions**: If you're unsure about something, ask! We're here to help

## Questions?

If you have questions about contributing, feel free to:

- Open a [GitHub Discussion](https://github.com/muhammadrivaldy/ainotes/discussions)
- Create an issue with the "question" label
- Check existing documentation in each component's README.md

## License

By contributing to AI Notes, you agree that your contributions will be licensed under the GNU General Public License v3.0 (GPLv3).

---

Thank you for contributing to AI Notes! Your efforts help make this project better for everyone.
