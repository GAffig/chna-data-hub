from sqlalchemy.orm import Session

from ..models import Source
from ..seed_data import CHNA_REFERENCE_SOURCES


def seed_reference_sources(db: Session) -> tuple[int, int]:
    inserted = 0
    skipped = 0

    for item in CHNA_REFERENCE_SOURCES:
        exists = db.query(Source).filter(Source.name == item["name"]).first()
        if exists:
            skipped += 1
            continue

        db.add(Source(**item))
        inserted += 1

    db.commit()
    return inserted, skipped
