from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.db import Base

class TestType(Base):
    __tablename__ = 'test_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    unit = Column(String(20), nullable=False)       # e.g., 'mL/kg/min', 'cm', 'kg', 'reps'
    category = Column(String(50), nullable=False)   # e.g., 'Cardiovascular', 'Flexibility', 'Strength'
    description = Column(Text, nullable=True)
    is_lower_better = Column(Boolean, default=False) # e.g., True for sprint timed running, False for jumps
    
    # Relationships
    records = relationship("TestRecord", back_populates="test_type", cascade="all, delete-orphan")
    standards = relationship("Standard", back_populates="test_type", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestType(id={self.id}, name='{self.name}', unit='{self.unit}')>"
