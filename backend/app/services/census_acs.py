import json
import os
from dataclasses import dataclass

import httpx
from sqlalchemy import delete
from sqlalchemy.orm import Session

from ..models import CommunityMetric, IngestionRun, RawDatasetSnapshot


@dataclass
class CensusPullResult:
    run_id: int
    source_name: str
    year: int
    state_fips: str
    records_loaded: int


def pull_census_acs_county_population(
    db: Session,
    year: int,
    state_fips: str,
    replace_existing: bool = True,
) -> CensusPullResult:
    source_name = "US Census ACS"
    dataset_name = "acs5"
    measure_code = "B01003_001E"
    measure_name = "Total Population"

    api_key = os.getenv("CENSUS_API_KEY", "").strip()

    params = {
        "get": f"NAME,{measure_code}",
        "for": "county:*",
        "in": f"state:{state_fips}",
    }
    if api_key:
        params["key"] = api_key

    url = f"https://api.census.gov/data/{year}/acs/{dataset_name}"
    response = httpx.get(url, params=params, timeout=30.0)
    response.raise_for_status()
    rows = response.json()

    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError("Unexpected Census API response format")

    headers = rows[0]
    data_rows = rows[1:]

    if replace_existing:
        db.execute(
            delete(CommunityMetric).where(
                CommunityMetric.source_name == source_name,
                CommunityMetric.measure_code == measure_code,
                CommunityMetric.year == year,
                CommunityMetric.geo_id.like(f"{state_fips}%"),
            )
        )

    loaded = 0
    for values in data_rows:
        row = dict(zip(headers, values))
        state = row.get("state", "")
        county = row.get("county", "")
        geo_id = f"{state}{county}"
        raw_value = row.get(measure_code)

        if raw_value in (None, "", "null"):
            continue

        db.add(
            CommunityMetric(
                source_name=source_name,
                measure_code=measure_code,
                measure_name=measure_name,
                unit="count",
                year=year,
                geo_id=geo_id,
                geo_name=row.get("NAME", geo_id),
                value=float(raw_value),
            )
        )
        loaded += 1

    db.add(
        RawDatasetSnapshot(
            source_name=source_name,
            dataset_name=dataset_name,
            geography_level="County",
            year=year,
            payload_json=json.dumps(data_rows),
        )
    )

    run = IngestionRun(
        source_name=source_name,
        run_status="success",
        record_count=loaded,
        notes=f"ACS {dataset_name} {year} county population for state {state_fips}",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return CensusPullResult(
        run_id=run.id,
        source_name=source_name,
        year=year,
        state_fips=state_fips,
        records_loaded=loaded,
    )
