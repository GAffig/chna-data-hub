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
