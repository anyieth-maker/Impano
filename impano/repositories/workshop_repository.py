"""SQL for the workshops and workshop_registrations tables."""

from __future__ import annotations

from typing import List, Optional

from impano.database import Database
from impano.models import Registration, Workshop

_SELECT = """
    SELECT w.*, tp.name AS talent_path, h.full_name AS host_name,
           (SELECT COUNT(*) FROM workshop_registrations r WHERE r.workshop_id = w.id) AS registered
    FROM workshops w
    LEFT JOIN talent_paths tp ON tp.id = w.talent_path_id
    LEFT JOIN users h ON h.id = w.host_id
"""


class WorkshopRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    # ------------------------------------------------------------ workshops
    def create(self, title: str, description: str, talent_path_id: Optional[int],
               location: str, event_date: str, capacity: int,
               host_id: Optional[int] = None) -> int:
        return self.db.insert(
            """INSERT INTO workshops
                   (title, description, talent_path_id, location, event_date, capacity, host_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, description, talent_path_id, location, event_date, capacity, host_id),
        )

    def get(self, workshop_id: int) -> Optional[Workshop]:
        row = self.db.fetch_one(_SELECT + " WHERE w.id = ?", (workshop_id,))
        return Workshop.from_row(row) if row else None

    def list_upcoming(self, today: str) -> List[Workshop]:
        rows = self.db.fetch_all(_SELECT + " WHERE w.event_date >= ? ORDER BY w.event_date", (today,))
        return [Workshop.from_row(r) for r in rows]

    def list_all(self) -> List[Workshop]:
        return [Workshop.from_row(r) for r in self.db.fetch_all(_SELECT + " ORDER BY w.event_date")]

    def list_by_host(self, host_id: int) -> List[Workshop]:
        rows = self.db.fetch_all(_SELECT + " WHERE w.host_id = ? ORDER BY w.event_date", (host_id,))
        return [Workshop.from_row(r) for r in rows]

    def update(self, workshop_id: int, title: str, description: str,
               talent_path_id: Optional[int], location: str, event_date: str,
               capacity: int) -> bool:
        cur = self.db.execute(
            """UPDATE workshops SET title = ?, description = ?, talent_path_id = ?,
                                    location = ?, event_date = ?, capacity = ?
               WHERE id = ?""",
            (title, description, talent_path_id, location, event_date, capacity, workshop_id),
        )
        return cur.rowcount > 0

    def delete(self, workshop_id: int) -> bool:
        return self.db.execute("DELETE FROM workshops WHERE id = ?", (workshop_id,)).rowcount > 0

    # --------------------------------------------------------- registrations
    def register(self, workshop_id: int, user_id: int, attendee_name: str, phone: str) -> int:
        return self.db.insert(
            """INSERT INTO workshop_registrations (workshop_id, user_id, attendee_name, phone)
               VALUES (?, ?, ?, ?)""",
            (workshop_id, user_id, attendee_name, phone),
        )

    def is_registered(self, workshop_id: int, user_id: int) -> bool:
        return bool(self.db.scalar(
            "SELECT 1 FROM workshop_registrations WHERE workshop_id = ? AND user_id = ?",
            (workshop_id, user_id),
        ))

    def registrations_for_user(self, user_id: int) -> List[Registration]:
        rows = self.db.fetch_all(
            """SELECT r.*, w.title AS workshop_title, w.event_date, w.location
               FROM workshop_registrations r
               JOIN workshops w ON w.id = r.workshop_id
               WHERE r.user_id = ? ORDER BY w.event_date""",
            (user_id,),
        )
        return [Registration.from_row(r) for r in rows]

    def attendees(self, workshop_id: int) -> List[Registration]:
        rows = self.db.fetch_all(
            "SELECT * FROM workshop_registrations WHERE workshop_id = ? ORDER BY registered_at",
            (workshop_id,),
        )
        return [Registration.from_row(r) for r in rows]

    def cancel(self, workshop_id: int, user_id: int) -> bool:
        cur = self.db.execute(
            "DELETE FROM workshop_registrations WHERE workshop_id = ? AND user_id = ?",
            (workshop_id, user_id),
        )
        return cur.rowcount > 0

    def count_registrations(self) -> int:
        return self.db.scalar("SELECT COUNT(*) FROM workshop_registrations")
