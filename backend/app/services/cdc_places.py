import json
from dataclasses import dataclass

import httpx
from sqlalchemy import delete
from sqlalchemy.orm import Session

from ..models import CommunityMetric, IngestionRun, RawDatasetSnapshot


@dataclass
class PlacesPullResult:
    run_id: int
    source_name: str
    year: int
    state_abbr: str
    records_loaded: int


def pull_cdc_places_county_measures(
    db: Session,
    year: int,
    state_abbr: str,
    replace_existing: bool = True,
) -> PlacesPullResult:
    source_name = "CDC PLACES"
    dataset_name = "county_data"
    dataset_id = "swc5-untb"  # PLACES: Local Data for Better Health, County Data, 2025 release

    state_abbr = state_abbr.upper()

    params = {
        "$select": "locationid,locationname,measureid,measure,data_value,data_value_unit,year,stateabbr",
        "$where": f"stateabbr='{state_abbr}' AND year='{year}' AND data_value IS NOT NULL",
        "$limit": 50000,
    }

    url = f"https://data.cdc.gov/resource/{dataset_id}.json"
    response = httpx.get(url, params=params, timeout=60.0)
    response.raise_for_status()
    rows = response.json()

    if not isinstance(rows, list):
        raise ValueError("Unexpected CDC PLACES response format")

    state_fips_prefix = ""
    if rows:
        first_geo = rows[0].get("locationid", "")
        if len(first_geo) >= 2:
            state_fips_prefix = first_geo[:2]

    if replace_existing and state_fips_prefix:
        db.execute(
            delete(CommunityMetric).where(
                CommunityMetric.source_name == source_name,
                CommunityMetric.year == year,
                CommunityMetric.geo_id.like(f"{state_fips_prefix}%"),
            )
        )

    loaded = 0
    for row in rows:
        raw_value = row.get("data_value")
        if raw_value in (None, "", "null"):
            continue

        try:
            value = float(raw_value)
        except ValueError:
            continue

        db.add(
            CommunityMetric(
                source_name=source_name,
                measure_code=row.get("measureid", "UNKNOWN"),
                measure_name=row.get("measure", "Unknown Measure"),
                unit=row.get("data_value_unit", "percent"),
                year=year,
                geo_id=row.get("locationid", ""),
                geo_name=row.get("locationname", row.get("locationid", "")),
                value=value,
            )
        )
        loaded += 1

    db.add(
        RawDatasetSnapshot(
            source_name=source_name,
            dataset_name=dataset_name,
            geography_level="County",
            year=year,
            payload_json=json.dumps(rows),
        )
    )

    run = IngestionRun(
        source_name=source_name,
        run_status="success",
        record_count=loaded,
        notes=f"CDC PLACES county measures for {state_abbr} ({year})",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return PlacesPullResult(
        run_id=run.id,
        source_name=source_name,
        year=year,
        state_abbr=state_abbr,
        records_loaded=loaded,
    )
