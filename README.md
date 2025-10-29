
# Carrom

> NOTE: This repository is private. Access is restricted — request access from the repository owner (bagheerabackend) if you need to clone or contribute.

Carrom is a web-based implementation of the classic tabletop Carrom game. This repository contains:
- A client-side web UI (HTML/CSS/JS) for gameplay and visualization.
- A Python-based backend API to manage game sessions, validate moves, and persist state.
- An admin Dashboard for monitoring games, users and metrics.
- Docker configuration to run components in containers.

Language composition (approximate):
- HTML: 79%
- Python: 20.8%
- Dockerfile: 0.2%

This README covers how to run the project locally (client, API, dashboard), common API endpoints, Docker usage, and development notes.

## Table of contents
- [About](#about)
- [Status & access](#status--access)
- [Repository layout (typical)](#repository-layout-typical)
- [Prerequisites](#prerequisites)
- [Getting started](#getting-started)
  - [Clone / access (private repo)](#clone--access-private-repo)
  - [Run the API (Python)](#run-the-api-python)
  - [Run the Dashboard](#run-the-dashboard)
  - [Run the Client](#run-the-client)
  - [Run with Docker](#run-with-docker)
- [API overview (high-level)](#api-overview-high-level)
- [Environment & configuration](#environment--configuration)
- [Development notes & suggestions](#development-notes--suggestions)
- [Contributing (private repo)](#contributing-private-repo)
- [Security & sensitive data](#security--sensitive-data)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

## About
Carrom is a multiplayer board game where players flick disks (carrommen) to sink them into corner pockets. This project provides a browser client to play locally or connect to multiplayer sessions backed by a Python API and optionally managed via a Dashboard.

## Status & access
- Visibility: PRIVATE
- Primary languages: HTML (frontend), Python (backend), Dockerfile (containerization)
- If you need repository access, contact bagheerabackend to be added as a collaborator.

## Repository layout (typical)
Adjust paths below to match actual repository structure:
- /api or /server — Python backend (Flask/FastAPI/Django)
- /dashboard — admin UI (React/Vue/static)
- Dockerfile(s) or /docker — container definitions
- /docs — API specs, ER diagrams, design notes
- README.md — this file

## Prerequisites
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Python 3.9+ (if backend uses Python)
- pip or poetry for Python dependencies
- Optional: Docker & Docker Compose for containerized runs

## Getting started

### Clone / access (private repo)
Request access from the repository owner, then clone:
- HTTPS:
  git clone https://github.com/bagheerabackend/Carrom.git
- SSH:
  git clone git@github.com:bagheerabackend/Carrom.git
- Or with GitHub CLI:
  gh repo clone bagheerabackend/Carrom

Authenticate when prompted.

### Run the API (Python)
1. Change into the API directory (example):
   cd appname
2. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
3. Install dependencies:
   pip install -r requirements.txt
   (or use poetry/pipenv if present)
4. Copy and edit environment template:
   cp .env.example .env
   Edit .env with DB, secrets, and configuration values.
5. Run the API (examples):
   - For Flask:
     export FLASK_APP=app.py
     flask run
   - For FastAPI (uvicorn):
     uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Check the API directory for a dedicated README or start script for exact commands.

### Run with Docker
A Dockerfile exists to containerize components; you can build and run locally:

- Build an image (example for API):
  docker build

If a docker-compose.yml is present:
  docker-compose up --build

Ensure environment variables and DB connections are configured for containers.

## API overview (high-level)
Below are suggested endpoints typical for a carrom game API. Update to match your actual routes.

- Authentication
  - POST /api/v1/auth/login
  - POST /api/v1/auth/register
- Game sessions
  - POST /api/v1/games — create a new game
  - GET /api/v1/games — list available games
  - GET /api/v1/games/{id} — fetch game state
  - POST /api/v1/games/{id}/join — join a game
  - POST /api/v1/games/{id}/move — submit a shot/move (payload: player, vector/force, timestamp)
  - POST /api/v1/games/{id}/end — end or forfeit a game
- Player & stats
  - GET /api/v1/players/{id}
  - GET /api/v1/stats — leaderboard, win/loss
- Admin / Dashboard
  - GET /api/v1/admin/games — list active/recent games
  - GET /api/v1/admin/stats — metrics and telemetry
  - POST /api/v1/admin/users/{id}/suspend

If you have OpenAPI/Swagger or Postman collections, place them in /docs and link from here.

Realtime play: For responsive multiplayer, consider WebSockets (Socket.IO or ws) for live shot updates and syncing physics/state between clients and server.

## Environment & configuration
Use a .env file for runtime configuration.

Include a .env.example (without secrets) to document required keys.

## Development notes & suggestions
- Keep core physics and game rules separated from transport layer to facilitate unit testing.
- Add unit and integration tests for move validation and scoring (pytest recommended for Python).
- Use Docker Compose to run DB + API + Dashboard locally for realistic testing.
- Add CI to run tests and linting (e.g., GitHub Actions).
- Consider TypeScript for the dashboard/client for stronger types.
- Improve accessibility for UI (keyboard support, ARIA).

## Contributing (private repo)
- Request access from the owner to contribute.
- Branching workflow:
  git checkout -b feature/your-feature
- Run tests and linters before opening a PR.
- Provide screenshots or short recordings for UI changes.

If you don't have permission to create branches or PRs, request collaborator access.

## Security & sensitive data
- Never commit secrets, API keys or private certs.
- Store secrets in environment variables or a secrets manager.
- Rotate compromised secrets immediately and notify collaborators.

## License
No license file is included in repository metadata. Add a LICENSE if you plan to make the repository public (MIT, Apache-2.0, etc.).

## Contact
Repository: https://github.com/bagheerabackend/Carrom  
Owner: bagheerabackend — open an issue or contact the owner to request access.

## Acknowledgements
- Classic Carrom rules and community resources.
- Third-party libraries, graphics or assets used — please include attribution in the repo.
