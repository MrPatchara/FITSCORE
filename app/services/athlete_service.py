"""
AthleteService — Service layer for Athlete and Group CRUD operations.
Provides search, filter, bulk group assignment, and data access methods.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.athlete import Athlete, Group
from app.core.db import db_session


class AthleteService:
    """Handles all database operations related to Athletes and Groups."""

    def __init__(self, session: Optional[Session] = None):
        self._session = session or db_session

    @property
    def session(self) -> Session:
        return self._session

    # ═══════════════════════════════════════════════════════════════════════════
    # ATHLETE CRUD
    # ═══════════════════════════════════════════════════════════════════════════

    def get_all_athletes(
        self,
        search: str = "",
        gender_filter: str = "",
        group_filter: Optional[int] = None,
    ) -> list[Athlete]:
        """
        Retrieve athletes with optional search and filter criteria.
        
        Args:
            search: Search term matched against first_name and last_name.
            gender_filter: Filter by gender value (e.g. 'Male', 'Female').
            group_filter: Filter by group ID. Use -1 for athletes without a group.
        """
        q = self.session.query(Athlete)

        if search:
            term = f"%{search}%"
            q = q.filter(
                or_(
                    Athlete.first_name.ilike(term),
                    Athlete.last_name.ilike(term),
                )
            )

        if gender_filter:
            q = q.filter(Athlete.gender == gender_filter)

        if group_filter is not None:
            if group_filter == -1:
                q = q.filter(Athlete.group_id.is_(None))
            else:
                q = q.filter(Athlete.group_id == group_filter)

        return q.order_by(Athlete.id.asc()).all()

    def get_athlete_by_id(self, athlete_id: int) -> Optional[Athlete]:
        return self.session.query(Athlete).get(athlete_id)

    def create_athlete(
        self,
        first_name: str,
        last_name: str,
        gender: str,
        date_of_birth,
        group_id: Optional[int] = None,
        notes: str = "",
        address: str = "",
        phone: str = "",
        email: str = "",
        photo_path: Optional[str] = None,
        photo_bytes: Optional[bytes] = None,
    ) -> Athlete:
        athlete = Athlete(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            gender=gender,
            date_of_birth=date_of_birth,
            group_id=group_id,
            notes=notes.strip(),
            address=address.strip(),
            phone=phone.strip(),
            email=email.strip(),
            photo_path=photo_path,
            photo_bytes=photo_bytes,
        )
        self.session.add(athlete)
        self.session.commit()
        return athlete

    def update_athlete(
        self,
        athlete_id: int,
        first_name: str,
        last_name: str,
        gender: str,
        date_of_birth,
        group_id: Optional[int] = None,
        notes: str = "",
        address: str = "",
        phone: str = "",
        email: str = "",
        photo_path: Optional[str] = None,
        photo_bytes: Optional[bytes] = None,
    ) -> Optional[Athlete]:
        athlete = self.get_athlete_by_id(athlete_id)
        if not athlete:
            return None
        athlete.first_name = first_name.strip()
        athlete.last_name = last_name.strip()
        athlete.gender = gender
        athlete.date_of_birth = date_of_birth
        athlete.group_id = group_id
        athlete.notes = notes.strip()
        athlete.address = address.strip()
        athlete.phone = phone.strip()
        athlete.email = email.strip()
        athlete.photo_path = photo_path
        athlete.photo_bytes = photo_bytes
        self.session.commit()
        return athlete

    def delete_athlete(self, athlete_id: int) -> bool:
        athlete = self.get_athlete_by_id(athlete_id)
        if not athlete:
            return False
        self.session.delete(athlete)
        self.session.commit()
        return True

    def move_athletes_to_group(
        self, athlete_ids: list[int], group_id: Optional[int]
    ) -> int:
        """
        Move multiple athletes to a group. Pass group_id=None to remove from group.
        Returns the number of athletes updated.
        """
        count = 0
        for aid in athlete_ids:
            athlete = self.get_athlete_by_id(aid)
            if athlete:
                athlete.group_id = group_id
                count += 1
        self.session.commit()
        return count

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP CRUD
    # ═══════════════════════════════════════════════════════════════════════════

    def get_all_groups(self) -> list[Group]:
        return self.session.query(Group).order_by(Group.name.asc()).all()

    def get_group_by_id(self, group_id: int) -> Optional[Group]:
        return self.session.query(Group).get(group_id)

    def create_group(self, **kwargs) -> Group:
        """Create a new group with any combination of fields."""
        # Strip string fields
        for key in list(kwargs.keys()):
            if isinstance(kwargs[key], str):
                kwargs[key] = kwargs[key].strip()
        group = Group(**kwargs)
        self.session.add(group)
        self.session.commit()
        return group

    def update_group(self, group_id: int, **kwargs) -> Optional[Group]:
        """Update group fields. Only provided kwargs are updated."""
        group = self.get_group_by_id(group_id)
        if not group:
            return None
        for key, value in kwargs.items():
            if hasattr(group, key):
                if isinstance(value, str):
                    value = value.strip()
                setattr(group, key, value)
        self.session.commit()
        return group

    def delete_group(self, group_id: int) -> bool:
        """
        Delete a group. Athletes in this group will have group_id set to NULL
        automatically due to the ondelete='SET NULL' foreign key constraint.
        """
        group = self.get_group_by_id(group_id)
        if not group:
            return False
        # Manually set athletes to no group before deleting
        # (cascade='all, delete-orphan' would delete athletes, so we detach first)
        for athlete in group.athletes:
            athlete.group_id = None
        self.session.commit()
        self.session.delete(group)
        self.session.commit()
        return True

    def group_name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a group name already exists (case-insensitive)."""
        q = self.session.query(Group).filter(Group.name.ilike(name.strip()))
        if exclude_id is not None:
            q = q.filter(Group.id != exclude_id)
        return q.first() is not None
