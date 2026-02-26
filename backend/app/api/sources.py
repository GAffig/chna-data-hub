from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Source
from ..schemas import SourceCreate, SourceRead

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
