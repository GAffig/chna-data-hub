from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Source
from ..schemas import SeedResponse, SourceCreate, SourceRead
from ..services.seed import seed_reference_sources

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceRead])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).order_by(Source.name.asc()).all()


@router.post("", response_model=SourceRead)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    source = Source(**payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.post("/seed", response_model=SeedResponse)
def seed_sources(db: Session = Depends(get_db)):
    inserted, skipped = seed_reference_sources(db)
    return SeedResponse(inserted=inserted, skipped=skipped)
