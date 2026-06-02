from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.db import Base

class Group(Base):
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # ── Address ──
    address = Column(Text, nullable=True)           # ที่อยู่ (บ้านเลขที่ ซอย ถนน)
    province = Column(String(50), nullable=True)     # จังหวัด
    district = Column(String(50), nullable=True)     # อำเภอ/เขต
    sub_district = Column(String(50), nullable=True) # ตำบล/แขวง
    postal_code = Column(String(10), nullable=True)  # รหัสไปรษณีย์

    # ── Coordinator (ผู้ประสานงาน) ──
    coordinator_name = Column(String(100), nullable=True)
    coordinator_phone = Column(String(20), nullable=True)
    coordinator_email = Column(String(100), nullable=True)

    # ── Supervisor (ผู้ควบคุมการทดสอบ) ──
    supervisor_name = Column(String(100), nullable=True)
    supervisor_phone = Column(String(20), nullable=True)
    supervisor_email = Column(String(100), nullable=True)
    
    # Relationship to athletes in this group
    athletes = relationship("Athlete", back_populates="group", cascade="all, delete-orphan")

    @property
    def full_address(self) -> str:
        """Returns formatted full address string."""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.sub_district:
            parts.append(f"แขวง/ตำบล {self.sub_district}")
        if self.district:
            parts.append(f"เขต/อำเภอ {self.district}")
        if self.province:
            parts.append(f"จ.{self.province}")
        if self.postal_code:
            parts.append(self.postal_code)
        return "  ".join(parts) if parts else ""

    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}')>"

class Athlete(Base):
    __tablename__ = 'athletes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=False)  # 'Male', 'Female', 'Other'
    date_of_birth = Column(Date, nullable=False)
    photo_path = Column(String(255), nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='SET NULL'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # ── Contact details ──
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    group = relationship("Group", back_populates="athletes")
    records = relationship("TestRecord", back_populates="athlete", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        today = date.today()
        dob = self.date_of_birth
        # Calculate age correctly considering birth date in the current year
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @property
    def dob_buddhist_era(self) -> str:
        """Returns formatted date of birth in Buddhist Era."""
        if not self.date_of_birth:
            return "—"
        d = self.date_of_birth
        return f"{d.strftime('%d/%m')}/{d.year + 543}"

    def __repr__(self):
        return f"<Athlete(id={self.id}, name='{self.full_name}', age={self.age})>"
