# CHNA Data Hub

Manager-friendly CHNA data retrieval app for Ballad Population Health teams.

## What This Version Delivers

- Multi-page web app for non-technical users:
  - `Explorer` (state/county selection -> indicators -> CSV download)
  - `Smart Search` (plain-language style query with source-cited results)
  - `Settings` (health check, source seed, connector refresh, run history)
- Focused geography defaults for Northeast Tennessee and Southwest Virginia
- Persistent source attribution bar in UI
- Source registry seeded from your BRMC CHNA references
- Connector-backed ingestion from Census ACS and CDC PLACES

## Tech Stack

- `backend/`: FastAPI + SQLAlchemy
- `frontend/`: static multi-page UI (`index.html`, `search.html`, `settings.html`)
- `.github/workflows/ci.yml`: lint + tests on push/PR

## Design Direction

The UI uses Ballad website visual cues:
- Primary palette anchored on Ballad blues (`#006bb6`, `#004ea0`, `#0096ff`)
- Clean white panels and clear typography hierarchy
- Task-first workflow (step-by-step retrieval and export)

## Quick Start

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
python -m http.server 8080
```

Open `http://localhost:8080`.

## Main API Endpoints

- `GET /health`
- `GET /sources`
- `POST /sources`
- `POST /sources/seed`
- `GET /runs`
- `POST /runs`
- `POST /connectors/census-acs/pull`
- `POST /connectors/cdc-places/pull`
- `GET /geography/options`
- `GET /search`
- `GET /metrics`
- `GET /metrics/facets`
- `GET /metrics/export/csv`

### `/metrics` filters

- `year`
- `source_name`
- `measure_code`
- `state_fips`
- `county_geo_id`
- `geo_prefix`
- `limit` (1 to 5000)

## CHNA Topic Guidance Included

The interface includes quick topic presets aligned to your CHNA priorities and appendix direction, including:
- Chronic disease (diabetes, heart disease, cancer)
- Behavioral/mental health and deaths of despair
- Overweight/obesity
- Access-related indicators

It is intentionally not limited to only those topics.

## Share With A Colleague

1. Start backend on your machine (`0.0.0.0:8000`).
2. Start frontend on your machine (`:8080`).
3. Share your host IP (example `http://192.168.1.20:8080`).
4. Teammate opens the URL on the same network.

If needed, set `APP_CORS_ORIGINS` in backend env to restrict allowed browser origins (default is `*` for easy pilot testing).

## Quality Checks

```bash
cd backend
python -m ruff check .
python -m pytest -q tests/test_health.py tests/test_seed_and_metrics.py tests/test_geography_and_search.py
```
