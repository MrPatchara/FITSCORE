from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.db import Base

class Standard(Base):
    __tablename__ = 'standards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_type_id = Column(Integer, ForeignKey('test_types.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)  # Determines if this standard interprets new results
    
    # Relationships
    test_type = relationship("TestType", back_populates="standards")
    rules = relationship("StandardRule", back_populates="standard", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Standard(id={self.id}, name='{self.name}', is_active={self.is_active})>"

class StandardRule(Base):
    __tablename__ = 'standard_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    standard_id = Column(Integer, ForeignKey('standards.id', ondelete='CASCADE'), nullable=False)
    gender = Column(String(10), nullable=False)          # 'Male', 'Female', 'All'
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)
    min_value = Column(Float, nullable=True)             # NULL means negative infinity
    max_value = Column(Float, nullable=True)             # NULL means positive infinity
    performance_level = Column(String(50), nullable=False) # e.g., 'Excellent', 'Good', 'Average', etc.
    color_code = Column(String(7), nullable=False)       # Hex code representation: '#2ECC71'
    score_points = Column(Integer, default=0)            # Point value for this bracket (0-100 or 1-5)
    
    # Relationships
    standard = relationship("Standard", back_populates="rules")

    def __repr__(self):
        return (f"<StandardRule(id={self.id}, standard_id={self.standard_id}, "
                f"gender='{self.gender}', age={self.min_age}-{self.max_age}, "
                f"range=[{self.min_value}, {self.max_value}], level='{self.performance_level}')>")
