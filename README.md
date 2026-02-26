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

## Current Endpoints

- `GET /health`
- `GET /sources`
- `POST /sources`
- `POST /sources/seed` (loads CHNA references from your BRMC reference list)
- `GET /runs`
- `POST /runs`
- `POST /connectors/census-acs/pull`
- `POST /connectors/cdc-places/pull`
- `GET /metrics`

## MVP Workflow

1. Seed approved reference sources:
```bash
curl -X POST http://localhost:8000/sources/seed
```

2. Pull Census ACS county population (TN by default):
```bash
curl -X POST http://localhost:8000/connectors/census-acs/pull \
  -H "Content-Type: application/json" \
  -d '{"year": 2024, "state_fips": "47", "replace_existing": true}'
```

3. Pull CDC PLACES county measures:
```bash
curl -X POST http://localhost:8000/connectors/cdc-places/pull \
  -H "Content-Type: application/json" \
  -d '{"year": 2025, "state_abbr": "TN", "replace_existing": true}'
```

4. Query standardized metric records:
```bash
curl "http://localhost:8000/metrics?year=2025&source_name=CDC%20PLACES"
```

Optionally set `CENSUS_API_KEY` in your environment before pulling Census data.

## Why this setup avoids dependency drift

- Pinned Python dependencies in `backend/requirements.txt`
- Containerized runtime in `docker-compose.yml`
- CI checks in GitHub Actions
- Explicit schema contracts in `data_contracts/`
