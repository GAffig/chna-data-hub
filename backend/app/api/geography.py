from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import CommunityMetric
from ..schemas import GeographyCounty, GeographyOptionsResponse, GeographyState

router = APIRouter(prefix="/geography", tags=["geography"])


STATE_MAP = {
    "47": {"abbr": "TN", "name": "Tennessee"},
    "51": {"abbr": "VA", "name": "Virginia"},
}

FOCUS_REGION_COUNTIES = [
    {"geo_id": "47019", "name": "Carter County", "state_fips": "47"},
    {"geo_id": "47059", "name": "Greene County", "state_fips": "47"},
    {"geo_id": "47067", "name": "Hancock County", "state_fips": "47"},
    {"geo_id": "47073", "name": "Hawkins County", "state_fips": "47"},
    {"geo_id": "47091", "name": "Johnson County", "state_fips": "47"},
    {"geo_id": "47163", "name": "Sullivan County", "state_fips": "47"},
    {"geo_id": "47171", "name": "Unicoi County", "state_fips": "47"},
    {"geo_id": "47179", "name": "Washington County", "state_fips": "47"},
    {"geo_id": "51027", "name": "Buchanan County", "state_fips": "51"},
    {"geo_id": "51051", "name": "Dickenson County", "state_fips": "51"},
    {"geo_id": "51077", "name": "Grayson County", "state_fips": "51"},
    {"geo_id": "51105", "name": "Lee County", "state_fips": "51"},
    {"geo_id": "51167", "name": "Russell County", "state_fips": "51"},
    {"geo_id": "51169", "name": "Scott County", "state_fips": "51"},
    {"geo_id": "51173", "name": "Smyth County", "state_fips": "51"},
    {"geo_id": "51185", "name": "Tazewell County", "state_fips": "51"},
    {"geo_id": "51191", "name": "Washington County", "state_fips": "51"},
    {"geo_id": "51195", "name": "Wise County", "state_fips": "51"},
]


@router.get("/options", response_model=GeographyOptionsResponse)
def geography_options(db: Session = Depends(get_db)):
    rows = (
        db.query(CommunityMetric.geo_id, CommunityMetric.geo_name)
        .distinct()
        .order_by(CommunityMetric.geo_name.asc())
        .all()
    )

    available = {}
    for row in rows:
        geo_id = str(row[0])
        if len(geo_id) >= 5 and geo_id[:2] in STATE_MAP:
            available[geo_id[:5]] = str(row[1])

    focus_ids = {item["geo_id"] for item in FOCUS_REGION_COUNTIES}
    counties: list[GeographyCounty] = []

    for item in FOCUS_REGION_COUNTIES:
        state = STATE_MAP[item["state_fips"]]
        counties.append(
            GeographyCounty(
                geo_id=item["geo_id"],
                name=item["name"],
                state_abbr=state["abbr"],
                state_fips=item["state_fips"],
                focus_region=True,
                available=item["geo_id"] in available,
            )
        )

    for geo_id, geo_name in available.items():
        if geo_id in focus_ids:
            continue
        state_fips = geo_id[:2]
        state = STATE_MAP.get(state_fips)
        if not state:
            continue
        counties.append(
            GeographyCounty(
                geo_id=geo_id,
                name=geo_name,
                state_abbr=state["abbr"],
                state_fips=state_fips,
                focus_region=False,
                available=True,
            )
        )

    counties.sort(key=lambda c: (not c.focus_region, c.state_abbr, c.name))
    states = [
        GeographyState(name=meta["name"], abbr=meta["abbr"], fips=fips)
        for fips, meta in STATE_MAP.items()
    ]

    return GeographyOptionsResponse(states=states, counties=counties)
