from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import CensusPullRequest, CensusPullResponse
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
