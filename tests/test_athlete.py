import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from app.core.db import Base
from app.models.athlete import Athlete
from app.services.athlete_service import AthleteService

@pytest.fixture
def db_session():
    """
    Creates an in-memory SQLite database and yields a session.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_create_athlete_with_photo_bytes(db_session):
    service = AthleteService(db_session)
    dummy_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR..."
    
    ath = service.create_athlete(
        first_name="สมชาย",
        last_name="ใจดี",
        gender="Male",
        date_of_birth=date(1995, 5, 20),
        notes="มีประวัติทดสอบดีเลิศ",
        photo_bytes=dummy_bytes
    )
    
    assert ath.id is not None
    assert ath.photo_bytes == dummy_bytes
    assert ath.photo_path is None

def test_update_athlete_photo_bytes(db_session):
    service = AthleteService(db_session)
    ath = service.create_athlete(
        first_name="สมหญิง",
        last_name="รักเรียน",
        gender="Female",
        date_of_birth=date(1998, 10, 15)
    )
    
    new_bytes = b"GIF89a..."
    updated_ath = service.update_athlete(
        athlete_id=ath.id,
        first_name="สมหญิง",
        last_name="รักเรียน",
        gender="Female",
        date_of_birth=date(1998, 10, 15),
        photo_bytes=new_bytes
    )
    
    assert updated_ath.photo_bytes == new_bytes
