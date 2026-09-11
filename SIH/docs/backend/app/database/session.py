from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.database.base import Base

# SQLite connect_args for multithreading
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG and False, # keep logs clean unless debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI dependency yielding a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables in the database."""
    # Import all models so Base.metadata is fully populated
    from app.models.inspection import (
        InspectionModel,
        ImageEvidenceModel,
        ExtractionModel,
        ComplianceResultModel,
        ReportModel,
    )
    Base.metadata.create_all(bind=engine)
