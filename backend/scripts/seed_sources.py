from app.db import SessionLocal
from app.services.seed import seed_reference_sources


def main() -> None:
    db = SessionLocal()
    try:
        inserted, skipped = seed_reference_sources(db)
        print(f"Seed complete. Inserted={inserted}, Skipped={skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
