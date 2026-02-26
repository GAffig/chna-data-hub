# AGENTS.md

## Purpose
Build and maintain a search-first CHNA research tool that feels like Google for structured public health and community data.

The product goal is:
- User enters natural language query (example: `Housing Quality data for NE TN counties`).
- System retrieves relevant county-level indicators from trusted sources.
- User filters by year/county/source/measure.
- User exports results with source attribution.

## Primary Users
- Population health analysts (daily users)
- CHNA report writers (weekly users)
- Non-technical leaders/managers (review users)

## Product Principles
1. Search-first UX, admin second.
2. Every value must be traceable to a source.
3. Keep county + year filters obvious and fast.
4. Prefer broad discoverability over rigid predefined dashboards.
5. Optimize for NE Tennessee and SW Virginia, but allow any available county.

## Current Repo Structure
- `backend/`: FastAPI APIs, connectors, normalization logic
- `frontend/`: static UI pages (`Explorer`, `Smart Search`, `Settings`)
- `data_contracts/`: schemas/templates
- `.github/workflows/`: CI checks

## Non-Negotiable Behaviors
1. Never return data without source attribution in UI.
2. Keep export deterministic (same filters => same rows).
3. Keep search + filters working for both focus region and non-focus counties.
4. Preserve backward compatibility on existing endpoints when possible.
5. Add tests for every new endpoint and every parsing rule change.

## CHNA Secondary Data Domains (from BRMC Appendix Tables)
Use these as first-class search domains:
- Demographics
- Housing and Families
- Physical Environment
- Clinical Care and Prevention
- COVID-19
- Workforce
- Health Behaviors
- Other Social and Economic Factors
- Social Determinants of Health (SDoH)
- Education
- Income and Economics

## High-Value Housing Metrics (must be searchable)
- Units affordable at 100% AMI
- Units affordable at 50% AMI
- Housing cost burden (30%)
- Severe housing cost burden (50%)
- Severe/substandard housing
- Median household value
- Median year structures built
- New building permits
- Older housing share
- Vacant housing units
- Overcrowded housing units

## Query Experience Requirements
For every query, system should infer:
- `topic_intent` (example: housing quality)
- `geography` (state/county/focus region)
- `time_scope` (year/range if provided)
- `candidate_metrics` (ranked)
- `candidate_sources` (ranked)

## Engineering Workflow
1. Update metric catalog + synonym map first.
2. Update retrieval/parser logic.
3. Update API response schema if needed.
4. Update UI result rendering + filters.
5. Add tests (parser, endpoint, integration).
6. Update roadmap/docs only after passing checks.

## Definition of Done (feature level)
- Lint passes (`ruff`)
- Tests pass (`pytest`)
- Search returns relevant rows for at least 3 realistic prompts
- Source bar shows real source links/citations
- CSV export works with active filters
- README and ROADMAP updated

