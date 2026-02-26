from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class SourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    url: HttpUrl
    category: str
    geography_level: str
    update_frequency: str
    owner: str
    citation: str


class SourceRead(SourceCreate):
    id: int

    model_config = {"from_attributes": True}


class RunCreate(BaseModel):
    source_name: str
    run_status: str
    record_count: int = Field(ge=0)
    notes: str = ""


class RunRead(RunCreate):
    id: int
    pulled_at: datetime

    model_config = {"from_attributes": True}


class SeedResponse(BaseModel):
    inserted: int
    skipped: int


class CensusPullRequest(BaseModel):
    year: int = Field(default=2024, ge=2009)
    state_fips: str = Field(default="47", min_length=2, max_length=2)
    replace_existing: bool = True


class CensusPullResponse(BaseModel):
    run_id: int
    source_name: str
    year: int
    state_fips: str
    records_loaded: int


class PlacesPullRequest(BaseModel):
    year: int = Field(default=2025, ge=2020)
    state_abbr: str = Field(default="TN", min_length=2, max_length=2)
    replace_existing: bool = True


class PlacesPullResponse(BaseModel):
    run_id: int
    source_name: str
    year: int
    state_abbr: str
    records_loaded: int


class CommunityMetricRead(BaseModel):
    id: int
    source_name: str
    measure_code: str
    measure_name: str
    unit: str
    year: int
    geo_id: str
    geo_name: str
    value: float
    pulled_at: datetime

    model_config = {"from_attributes": True}


class GeographyState(BaseModel):
    name: str
    abbr: str
    fips: str


class GeographyCounty(BaseModel):
    geo_id: str
    name: str
    state_abbr: str
    state_fips: str
    focus_region: bool
    available: bool


class GeographyOptionsResponse(BaseModel):
    states: list[GeographyState]
    counties: list[GeographyCounty]


class SourceAttributionRead(BaseModel):
    name: str
    url: str
    citation: str
    category: str


class MetricsFacetMeasure(BaseModel):
    measure_code: str
    measure_name: str


class MetricsFacetsResponse(BaseModel):
    years: list[int]
    sources: list[str]
    measures: list[MetricsFacetMeasure]
    counties: list[str]


class ResearchIntentRead(BaseModel):
    metric_key: str
    metric_name: str
    domain: str
    year: int | None
    is_latest: bool
    states: list[str]
    counties: list[str]
    geography_scope: str
    source_priority: list[str]


class ResearchResultRead(BaseModel):
    metric_key: str
    metric_name: str
    year: int
    geo_id: str
    geo_name: str
    value: float
    unit: str
    source_name: str
    source_url: str
    retrieved_at: datetime


class ResearchSearchResponse(BaseModel):
    query: str
    intent: ResearchIntentRead
    total_results: int
    items: list[ResearchResultRead]
    sources: list[SourceAttributionRead]
    note: str
