from datetime import date
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Text, String
from sqlalchemy.orm import relationship
from app.core.db import Base

class TestRecord(Base):
    __tablename__ = 'test_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id', ondelete='CASCADE'), nullable=False)
    test_type_id = Column(Integer, ForeignKey('test_types.id', ondelete='CASCADE'), nullable=False)
    test_date = Column(Date, default=date.today, nullable=False)
    value = Column(Float, nullable=False)
    interpreted_grade = Column(String(50), nullable=True) # Caches the interpretation level
    notes = Column(Text, nullable=True)
    
    # Relationships
    athlete = relationship("Athlete", back_populates="records")
    test_type = relationship("TestType", back_populates="records")

    def __repr__(self):
        return f"<TestRecord(id={self.id}, athlete_id={self.athlete_id}, test_type='{self.test_type.name if self.test_type else self.test_type_id}', value={self.value})>"
