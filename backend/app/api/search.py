import re

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import CommunityMetric, Source
from ..schemas import SearchResponse, SearchResultRead, SourceAttributionRead

router = APIRouter(prefix="/search", tags=["search"])


def _score_row(query: str, row: CommunityMetric, tokens: list[str]) -> float:
    q = query.lower()
    measure_code = row.measure_code.lower()
    measure_name = row.measure_name.lower()
    geo_name = row.geo_name.lower()
    source_name = row.source_name.lower()

    score = 0.0
    if q == measure_code:
        score += 10
    if q in measure_code:
        score += 6
    if q in measure_name:
        score += 5
    if q in source_name:
        score += 3
    if q in geo_name:
        score += 2

    for token in tokens:
        if token in measure_name:
            score += 2
        if token in source_name:
            score += 1
        if token in geo_name:
            score += 1

    return score


@router.get("", response_model=SearchResponse)
def search_metrics(
    q: str = Query(min_length=2),
    state_fips: str | None = Query(default=None, min_length=2, max_length=2),
    county_geo_id: str | None = Query(default=None, min_length=5, max_length=5),
    year: int | None = Query(default=None),
    source_name: str | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(CommunityMetric)

    if county_geo_id:
        query = query.filter(CommunityMetric.geo_id == county_geo_id)
    elif state_fips:
        query = query.filter(CommunityMetric.geo_id.like(f"{state_fips}%"))

    if year is not None:
        query = query.filter(CommunityMetric.year == year)
    if source_name:
        query = query.filter(CommunityMetric.source_name == source_name)

    tokens = [token for token in re.findall(r"[a-zA-Z0-9_]+", q.lower()) if len(token) > 1]
    like_filters = [
        CommunityMetric.measure_name.ilike(f"%{q}%"),
        CommunityMetric.measure_code.ilike(f"%{q}%"),
        CommunityMetric.geo_name.ilike(f"%{q}%"),
        CommunityMetric.source_name.ilike(f"%{q}%"),
    ]
    for token in tokens:
        like_filters.append(CommunityMetric.measure_name.ilike(f"%{token}%"))

    query = query.filter(or_(*like_filters)).order_by(CommunityMetric.pulled_at.desc()).limit(3000)
    rows = query.all()

    scored = []
    for row in rows:
        score = _score_row(q, row, tokens)
        if score <= 0:
            continue
        scored.append((score, row))

    scored.sort(key=lambda item: (item[0], item[1].year, item[1].geo_name), reverse=True)
    top = scored[:limit]

    items = [
        SearchResultRead(
            source_name=row.source_name,
            measure_code=row.measure_code,
            measure_name=row.measure_name,
            unit=row.unit,
            year=row.year,
            geo_id=row.geo_id,
            geo_name=row.geo_name,
            value=row.value,
            score=score,
        )
        for score, row in top
    ]

    source_names = sorted({item.source_name for item in items})
    source_rows = db.query(Source).filter(Source.name.in_(source_names)).all() if source_names else []
    source_map = {row.name: row for row in source_rows}

    attributions = []
    for source in source_names:
        row = source_map.get(source)
        attributions.append(
            SourceAttributionRead(
                name=source,
                url=row.url if row else "",
                citation=row.citation if row else "",
                category=row.category if row else "",
            )
        )

    return SearchResponse(
        query=q,
        total_results=len(items),
        items=items,
        sources=attributions,
    )
