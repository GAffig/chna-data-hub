import csv
import re
from io import StringIO

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import distinct
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import CommunityMetric
from ..schemas import CommunityMetricRead, MetricsFacetMeasure, MetricsFacetsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


def _parse_county_geo_ids(county_geo_ids: str | None) -> list[str]:
    if not county_geo_ids:
        return []

    valid = []
    for item in county_geo_ids.split(","):
        code = item.strip()
        if re.fullmatch(r"\d{5}", code):
            valid.append(code)
    return sorted(set(valid))


def _apply_metric_filters(
    query,
    *,
    year: int | None,
    source_name: str | None,
    measure_code: str | None,
    geo_prefix: str | None,
    state_fips: str | None,
    county_geo_id: str | None,
    county_geo_ids: str | None,
):
    if year is not None:
        query = query.filter(CommunityMetric.year == year)
    if source_name:
        query = query.filter(CommunityMetric.source_name == source_name)
    if measure_code:
        query = query.filter(CommunityMetric.measure_code == measure_code)
    if county_geo_id:
        query = query.filter(CommunityMetric.geo_id == county_geo_id)
    elif county_geo_ids:
        geo_ids = _parse_county_geo_ids(county_geo_ids)
        if geo_ids:
            query = query.filter(CommunityMetric.geo_id.in_(geo_ids))
    else:
        effective_geo_prefix = geo_prefix or state_fips
        if effective_geo_prefix:
            query = query.filter(CommunityMetric.geo_id.like(f"{effective_geo_prefix}%"))
    return query


@router.get("/facets", response_model=MetricsFacetsResponse)
def metrics_facets(
    state_fips: str | None = Query(default=None, min_length=2, max_length=2),
    county_geo_id: str | None = Query(default=None, min_length=5, max_length=5),
    county_geo_ids: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    base = db.query(CommunityMetric)
    base = _apply_metric_filters(
        base,
        year=None,
        source_name=None,
        measure_code=None,
        geo_prefix=None,
        state_fips=state_fips,
        county_geo_id=county_geo_id,
        county_geo_ids=county_geo_ids,
    )

    years = [
        int(y[0])
        for y in base.with_entities(distinct(CommunityMetric.year)).order_by(CommunityMetric.year.desc()).all()
    ]
    sources = [
        str(s[0])
        for s in base.with_entities(distinct(CommunityMetric.source_name)).order_by(CommunityMetric.source_name.asc()).all()
    ]
    counties = [
        str(c[0])
        for c in base.with_entities(distinct(CommunityMetric.geo_name)).order_by(CommunityMetric.geo_name.asc()).all()
    ]

    measure_rows = (
        base.with_entities(CommunityMetric.measure_code, CommunityMetric.measure_name)
        .distinct()
        .order_by(CommunityMetric.measure_name.asc())
        .limit(500)
        .all()
    )
    measures = [
        MetricsFacetMeasure(measure_code=str(row[0]), measure_name=str(row[1]))
        for row in measure_rows
    ]

    return MetricsFacetsResponse(years=years, sources=sources, measures=measures, counties=counties)


@router.get("/export/csv")
def export_metrics_csv(
    year: int | None = Query(default=None),
    source_name: str | None = Query(default=None),
    measure_code: str | None = Query(default=None),
    geo_prefix: str | None = Query(default=None),
    state_fips: str | None = Query(default=None, min_length=2, max_length=2),
    county_geo_id: str | None = Query(default=None, min_length=5, max_length=5),
    county_geo_ids: str | None = Query(default=None),
    limit: int = Query(default=2000, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    query = db.query(CommunityMetric)
    query = _apply_metric_filters(
        query,
        year=year,
        source_name=source_name,
        measure_code=measure_code,
        geo_prefix=geo_prefix,
        state_fips=state_fips,
        county_geo_id=county_geo_id,
        county_geo_ids=county_geo_ids,
    )
    rows = query.order_by(CommunityMetric.year.desc(), CommunityMetric.geo_id.asc()).limit(limit).all()

    out = StringIO()
    writer = csv.writer(out)
    writer.writerow([
        "source_name",
        "measure_code",
        "measure_name",
        "unit",
        "year",
        "geo_id",
        "geo_name",
        "value",
        "pulled_at",
    ])
    for row in rows:
        writer.writerow([
            row.source_name,
            row.measure_code,
            row.measure_name,
            row.unit,
            row.year,
            row.geo_id,
            row.geo_name,
            row.value,
            row.pulled_at.isoformat(),
        ])

    filename = "chna-metrics-export.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=out.getvalue(), media_type="text/csv", headers=headers)


@router.get("", response_model=list[CommunityMetricRead])
def list_metrics(
    year: int | None = Query(default=None),
    source_name: str | None = Query(default=None),
    measure_code: str | None = Query(default=None),
    geo_prefix: str | None = Query(default=None),
    state_fips: str | None = Query(default=None, min_length=2, max_length=2),
    county_geo_id: str | None = Query(default=None, min_length=5, max_length=5),
    county_geo_ids: str | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    query = db.query(CommunityMetric)
    query = _apply_metric_filters(
        query,
        year=year,
        source_name=source_name,
        measure_code=measure_code,
        geo_prefix=geo_prefix,
        state_fips=state_fips,
        county_geo_id=county_geo_id,
        county_geo_ids=county_geo_ids,
    )

    return query.order_by(CommunityMetric.year.desc(), CommunityMetric.geo_id.asc()).limit(limit).all()
