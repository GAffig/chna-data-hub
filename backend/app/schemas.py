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
