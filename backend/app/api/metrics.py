from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import CommunityMetric
from ..schemas import CommunityMetricRead

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=list[CommunityMetricRead])
def list_metrics(
    year: int | None = Query(default=None),
    source_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(CommunityMetric)

    if year is not None:
        query = query.filter(CommunityMetric.year == year)
    if source_name:
        query = query.filter(CommunityMetric.source_name == source_name)

    return query.order_by(CommunityMetric.year.desc(), CommunityMetric.geo_id.asc()).limit(1000).all()
