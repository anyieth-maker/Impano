"""SQL for the mentorship_requests table."""

from __future__ import annotations

from typing import List, Optional

from impano.database import Database
from impano.models import MentorshipRequest

_SELECT = """
    SELECT m.*, mem.full_name AS member_name, mem.phone AS member_phone,
           men.full_name AS mentor_name, men.phone AS mentor_phone
    FROM mentorship_requests m
    JOIN users mem ON mem.id = m.member_id
    JOIN users men ON men.id = m.mentor_id
"""


class MentorshipRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, member_id: int, mentor_id: int, message: str) -> int:
        return self.db.insert(
            "INSERT INTO mentorship_requests (member_id, mentor_id, message) VALUES (?, ?, ?)",
            (member_id, mentor_id, message),
        )

    def get(self, request_id: int) -> Optional[MentorshipRequest]:
        row = self.db.fetch_one(_SELECT + " WHERE m.id = ?", (request_id,))
        return MentorshipRequest.from_row(row) if row else None

    def has_pending(self, member_id: int, mentor_id: int) -> bool:
        return bool(self.db.scalar(
            """SELECT 1 FROM mentorship_requests
               WHERE member_id = ? AND mentor_id = ? AND status = 'pending'""",
            (member_id, mentor_id),
        ))

    def list_for_mentor(self, mentor_id: int) -> List[MentorshipRequest]:
        rows = self.db.fetch_all(
            _SELECT + " WHERE m.mentor_id = ? ORDER BY m.status = 'pending' DESC, m.created_at DESC",
            (mentor_id,),
        )
        return [MentorshipRequest.from_row(r) for r in rows]

    def list_for_member(self, member_id: int) -> List[MentorshipRequest]:
        rows = self.db.fetch_all(_SELECT + " WHERE m.member_id = ? ORDER BY m.created_at DESC", (member_id,))
        return [MentorshipRequest.from_row(r) for r in rows]

    def update_status(self, request_id: int, status: str) -> bool:
        cur = self.db.execute(
            "UPDATE mentorship_requests SET status = ? WHERE id = ?", (status, request_id)
        )
        return cur.rowcount > 0

    def delete(self, request_id: int) -> bool:
        return self.db.execute("DELETE FROM mentorship_requests WHERE id = ?", (request_id,)).rowcount > 0
