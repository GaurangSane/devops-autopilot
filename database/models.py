from sqlalchemy import (
    Column, String, Text, DateTime,
    JSON, create_engine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()

class Incident(Base):
    """
    Stores every incident and its full analysis.
    One row = one complete incident lifecycle.
    """
    __tablename__ = "incidents"

    incident_id    = Column(String, primary_key=True)
    status         = Column(String, default="queued")
    submitted_by   = Column(String, default="anonymous")
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Raw input
    raw_logs       = Column(Text)

    # Agent outputs
    log_analysis   = Column(Text, nullable=True)
    root_cause     = Column(Text, nullable=True)
    fixes          = Column(Text, nullable=True)
    runbook        = Column(Text, nullable=True)
    post_mortem    = Column(Text, nullable=True)

    # Metadata
    severity           = Column(String, nullable=True)
    affected_services  = Column(JSON, nullable=True)
    search_queries     = Column(JSON, nullable=True)

    # File paths
    runbook_path       = Column(String, nullable=True)
    post_mortem_path   = Column(String, nullable=True)

    # Error tracking
    errors             = Column(JSON, default=list)


def get_engine():
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://autopilot:autopilot123@localhost:5432/devops_autopilot"
    )
    print("DATABASE_URL =", db_url)
    return create_engine(db_url, echo=False)


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Creates all tables if they don't exist"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("✅ Database tables created")


if __name__ == "__main__":
    init_db()