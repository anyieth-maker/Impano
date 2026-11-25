"""Domain models (Classes & Objects).

Each class is a blueprint for one "Thing" the app keeps track of. Repositories
turn database rows into these objects with ``from_row``.
"""

from __future__ import annotations

from dataclasses import dataclass
from sqlite3 import Row
from typing import Optional

ROLES = ("member", "mentor", "admin")
CATEGORIES = ("Arts", "Trades", "Sports")


def _get(row: Row, key: str, default=None):
    """Read an optional column (joined columns are not always selected)."""
    return row[key] if key in row.keys() else default


@dataclass
class TalentPath:
    id: int
    name: str
    category: str

    @classmethod
    def from_row(cls, row: Row) -> "TalentPath":
        return cls(row["id"], row["name"], row["category"])


@dataclass
class User:
    id: int
    full_name: str
    username: str
    phone: str
    location: str
    role: str
    talent_path_id: Optional[int] = None
    talent_path: Optional[str] = None
    bio: str = ""

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_mentor(self) -> bool:
        return self.role == "mentor"

    @classmethod
    def from_row(cls, row: Row) -> "User":
        return cls(
            id=row["id"],
            full_name=row["full_name"],
            username=row["username"],
            phone=row["phone"],
            location=row["location"],
            role=row["role"],
            talent_path_id=row["talent_path_id"],
            talent_path=_get(row, "talent_path"),
            bio=row["bio"],
        )


@dataclass
class TrainingProgram:
    id: int
    name: str
    description: str
    talent_path_id: int
    center_name: str
    location: str
    contact: str
    talent_path: Optional[str] = None
    category: Optional[str] = None

    @classmethod
    def from_row(cls, row: Row) -> "TrainingProgram":
        return cls(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            talent_path_id=row["talent_path_id"],
            center_name=row["center_name"],
            location=row["location"],
            contact=row["contact"],
            talent_path=_get(row, "talent_path"),
            category=_get(row, "category"),
        )


@dataclass
class Workshop:
    id: int
    title: str
    description: str
    talent_path_id: Optional[int]
    location: str
    event_date: str
    capacity: int
    host_id: Optional[int] = None
    talent_path: Optional[str] = None
    host_name: Optional[str] = None
    registered: int = 0

    @property
    def seats_left(self) -> int:
        return max(self.capacity - self.registered, 0)

    @property
    def is_full(self) -> bool:
        return self.seats_left == 0

    @classmethod
    def from_row(cls, row: Row) -> "Workshop":
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            talent_path_id=row["talent_path_id"],
            location=row["location"],
            event_date=row["event_date"],
            capacity=row["capacity"],
            host_id=row["host_id"],
            talent_path=_get(row, "talent_path"),
            host_name=_get(row, "host_name"),
            registered=_get(row, "registered", 0) or 0,
        )


@dataclass
class Registration:
    id: int
    workshop_id: int
    user_id: int
    attendee_name: str
    phone: str
    registered_at: str
    workshop_title: Optional[str] = None
    event_date: Optional[str] = None
    location: Optional[str] = None

    @classmethod
    def from_row(cls, row: Row) -> "Registration":
        return cls(
            id=row["id"],
            workshop_id=row["workshop_id"],
            user_id=row["user_id"],
            attendee_name=row["attendee_name"],
            phone=row["phone"],
            registered_at=row["registered_at"],
            workshop_title=_get(row, "workshop_title"),
            event_date=_get(row, "event_date"),
            location=_get(row, "location"),
        )


@dataclass
class JobPosting:
    id: int
    title: str
    description: str
    talent_path_id: int
    location: str
    contact: str
    how_to_apply: str
    posted_by: Optional[int]
    is_open: bool
    created_at: str
    talent_path: Optional[str] = None
    category: Optional[str] = None
    poster_name: Optional[str] = None

    @classmethod
    def from_row(cls, row: Row) -> "JobPosting":
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            talent_path_id=row["talent_path_id"],
            location=row["location"],
            contact=row["contact"],
            how_to_apply=row["how_to_apply"],
            posted_by=row["posted_by"],
            is_open=bool(row["is_open"]),
            created_at=row["created_at"],
            talent_path=_get(row, "talent_path"),
            category=_get(row, "category"),
            poster_name=_get(row, "poster_name"),
        )


@dataclass
class MentorshipRequest:
    id: int
    member_id: int
    mentor_id: int
    message: str
    status: str
    created_at: str
    member_name: Optional[str] = None
    member_phone: Optional[str] = None
    mentor_name: Optional[str] = None
    mentor_phone: Optional[str] = None

    @classmethod
    def from_row(cls, row: Row) -> "MentorshipRequest":
        return cls(
            id=row["id"],
            member_id=row["member_id"],
            mentor_id=row["mentor_id"],
            message=row["message"],
            status=row["status"],
            created_at=row["created_at"],
            member_name=_get(row, "member_name"),
            member_phone=_get(row, "member_phone"),
            mentor_name=_get(row, "mentor_name"),
            mentor_phone=_get(row, "mentor_phone"),
        )
