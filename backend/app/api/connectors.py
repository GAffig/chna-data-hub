from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import (
    CensusPullRequest,
    CensusPullResponse,
    PlacesPullRequest,
    PlacesPullResponse,
)
from ..services.cdc_places import pull_cdc_places_county_measures
from ..services.census_acs import pull_census_acs_county_population

router = APIRouter(prefix="/connectors", tags=["connectors"])


@router.post("/census-acs/pull", response_model=CensusPullResponse)
def pull_census_acs(payload: CensusPullRequest, db: Session = Depends(get_db)):
    try:
        result = pull_census_acs_county_population(
            db=db,
            year=payload.year,
            state_fips=payload.state_fips,
            replace_existing=payload.replace_existing,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Census pull failed: {exc}") from exc

    return CensusPullResponse(
        run_id=result.run_id,
        source_name=result.source_name,
        year=result.year,
        state_fips=result.state_fips,
        records_loaded=result.records_loaded,
    )


@router.post("/cdc-places/pull", response_model=PlacesPullResponse)
def pull_cdc_places(payload: PlacesPullRequest, db: Session = Depends(get_db)):
    try:
        result = pull_cdc_places_county_measures(
            db=db,
            year=payload.year,
            state_abbr=payload.state_abbr,
            replace_existing=payload.replace_existing,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"CDC PLACES pull failed: {exc}") from exc

    return PlacesPullResponse(
        run_id=result.run_id,
        source_name=result.source_name,
        year=result.year,
        state_abbr=result.state_abbr,
        records_loaded=result.records_loaded,
    )
