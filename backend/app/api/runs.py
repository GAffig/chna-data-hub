from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import IngestionRun
from ..schemas import RunCreate, RunRead

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("", response_model=list[RunRead])
def list_runs(db: Session = Depends(get_db)):
    return db.query(IngestionRun).order_by(IngestionRun.pulled_at.desc()).all()


@router.post("", response_model=RunRead)
def create_run(payload: RunCreate, db: Session = Depends(get_db)):
    run = IngestionRun(**payload.model_dump())
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
