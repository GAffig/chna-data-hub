# ROADMAP.md

## CHNA Search Platform Blueprint

## Vision
Deliver a RAG-style CHNA data retrieval platform where analysts can type natural language questions and immediately get filterable, exportable, source-cited county/year data.

Example target query:
`Housing Quality data for NE TN counties`

Expected output:
- Ranked relevant indicators
- County-level values
- Year/source filters
- Downloadable CSV
- Citation/source strip

## Baseline (already in place)
- Source registry and ingestion run tracking
- Census ACS connector (population)
- CDC PLACES connector
- Explorer/Search/Settings UI shells
- Geography focus region support

## Data Guidance from BRMC Secondary Data Tables
Appendix domains extracted from `BRMC-combinedSecMetric.pdf`:
- Demographics
- Housing and Families
- Physical Environment
- Clinical Care and Prevention
- COVID-19 + Workforce
- Health Behaviors
- Other Social and Economic Factors
- SDoH
- Education
- Income and Economics

These domains define initial search intents and metric taxonomy.

---

## Phase 1: Metric Catalog + Search Relevance Core (Priority)
### Goal
Make natural language retrieval materially useful for CHNA research prompts.

### Deliverables
1. Canonical metric catalog table (`metric_catalog`)
- Fields: `measure_code`, `measure_name`, `domain`, `subdomain`, `unit`, `source_name`, `geo_level`, `year_min`, `year_max`, `is_active`

2. Intent/synonym table (`metric_synonyms`)
- Example mapping:
  - `housing quality` -> `substandard housing`, `cost burden`, `overcrowded`
  - `affordable housing` -> `AMI`, `cost burden`, `rent burden`
  - `mental health` -> `depression`, `poor mental health days`, `deaths of despair`

3. Search ranking upgrade
- Hybrid score = weighted keyword match + synonym match + domain boost + geography/time match.

4. New response metadata
- Return `matched_terms`, `domain`, `subdomain`, `why_matched`.

### Acceptance Criteria
- Query `Housing Quality data for NE TN counties` returns housing metrics first.
- Query `deaths of despair in SW VA` surfaces behavioral health metrics.
- Query `childcare burden` surfaces education/SDoH childcare metrics.

---

## Phase 2: Connector Expansion for CHNA Breadth
### Goal
Cover key non-health metrics needed for CHNA appendix-level analysis.

### Connector Backlog (ordered)
1. Census ACS Housing Pack
- Cost burden, rent/owner costs, overcrowding, occupancy/vacancy, home value, housing age.

2. Census ACS Income/Education Pack
- Median income, poverty bands, educational attainment, employment.

3. County Health Rankings ingestion
- Social/economic and health behavior comparatives.

4. USDA Food Access / Food insecurity proxies
- Low access and related indicators.

5. HUD (if stable extract/API for selected measures)
- Housing/affordability enrichment.

### Acceptance Criteria
- Each connector writes:
  - raw snapshot row
  - normalized metric rows in `community_metrics`
  - ingestion run record
- Metrics become searchable within same UX.

---

## Phase 3: Geography + Filter Intelligence
### Goal
Make place and time filtering effortless for non-technical users.

### Deliverables
1. Query parser geography extraction
- Recognize:
  - `NE TN`, `SW VA`, specific county names, state abbreviations.

2. Smart defaults
- If query has no county, default to focus region counties.
- If query has no year, default to latest available.

3. Facet panel improvements
- Domain
- Subdomain
- Source
- Year
- Geography

### Acceptance Criteria
- User can run query without touching filters and still get useful scoped results.

---

## Phase 4: RAG Layer for Source Text + Explainability
### Goal
Add explainable retrieval reasoning and richer source grounding.

### Deliverables
1. Vector index over:
- metric definitions
- source descriptions
- CHNA methodology/support docs

2. Retrieval pipeline
- Candidate generation from vector + keyword
- Re-ranking with structured constraints (geo/year/source availability)

3. Explainability block in UI
- `Matched because...`
- `Source confidence`
- `Data freshness`

### Acceptance Criteria
- Search explanations are understandable to a manager.
- Top results are clearly connected to user wording.

---

## Phase 5: Analyst Productivity + Governance
### Goal
Make report production and collaboration faster.

### Deliverables
1. Saved searches
2. Export bundles (CSV + citation list)
3. Runbook style appendix export template
4. Basic role model (viewer/editor/admin)
5. Data quality checks dashboard

### Acceptance Criteria
- Analyst can generate export package for report section in < 5 minutes.

---

## Implementation Sequence (Concrete)
1. Build catalog + synonym tables.
2. Backfill catalog from current `community_metrics`.
3. Add scoring/ranking update to `/search`.
4. Add Census ACS Housing connector.
5. Add domain/subdomain filters in Explorer + Search pages.
6. Add search explanations and source confidence.
7. Add saved searches and citation export.

---

## Test Plan
### Unit
- Query parsing
- Synonym expansion
- Relevance scoring

### API
- `/search` with realistic CHNA prompts
- `/metrics` with county/year/domain filters
- connector ingestion success/failure paths

### UX
- Explorer happy path (state -> county -> year -> export)
- Smart Search with source bar verification
- Settings connector refresh actions

### Regression
- Existing endpoints remain stable for current UI flows

---

## First Three Queries to Certify Before Pilot
1. `Housing Quality data for NE TN counties`
2. `Behavioral health and deaths of despair in SW VA 2022`
3. `Poverty and childcare burden in Sullivan County`

If these three produce clearly relevant, filterable, exportable, source-cited results, the pilot is ready.

