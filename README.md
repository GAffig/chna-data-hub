# CHNA Data Hub

GitHub-ready monorepo for CHNA source management, ingestion tracking, and team data access.

## Structure

- `backend/`: FastAPI + PostgreSQL API
- `frontend/`: lightweight web UI
- `data_contracts/`: source and metric schema contracts
- `.github/workflows/`: CI pipelines
- `infra/`: deployment placeholders

## Quick Start (Docker)

```bash
docker compose up --build
```

Services:
- API: http://localhost:8000/docs
- Frontend: http://localhost:8080
- Postgres: localhost:5432

## Local Dev (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

Serve files in `frontend/` with any static server.

## Initial Endpoints

- `GET /health`
- `GET /sources`
- `POST /sources`
- `GET /runs`
- `POST /runs`

## Why this setup avoids dependency drift

- Pinned Python dependencies in `backend/requirements.txt`
- Containerized runtime in `docker-compose.yml`
- CI checks in GitHub Actions
- Explicit schema contracts in `data_contracts/`
