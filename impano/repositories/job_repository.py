"""SQL for the job_postings table."""

from __future__ import annotations

from typing import List, Optional

from impano.database import Database
from impano.models import JobPosting

_SELECT = """
    SELECT j.*, tp.name AS talent_path, tp.category AS category,
           u.full_name AS poster_name
    FROM job_postings j
    JOIN talent_paths tp ON tp.id = j.talent_path_id
    LEFT JOIN users u ON u.id = j.posted_by
"""


class JobRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, title: str, description: str, talent_path_id: int, location: str,
               contact: str, how_to_apply: str, posted_by: Optional[int]) -> int:
        return self.db.insert(
            """INSERT INTO job_postings
                   (title, description, talent_path_id, location, contact, how_to_apply, posted_by)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, description, talent_path_id, location, contact, how_to_apply, posted_by),
        )

    def get(self, job_id: int) -> Optional[JobPosting]:
        row = self.db.fetch_one(_SELECT + " WHERE j.id = ?", (job_id,))
        return JobPosting.from_row(row) if row else None

    def search_by_category(self, category: str, location: str = "",
                           open_only: bool = True) -> List[JobPosting]:
        """Feature 3: filter postings by skill category (Arts / Trades / Sports)."""
        sql = _SELECT + " WHERE tp.category = ? AND j.location LIKE ?"
        if open_only:
            sql += " AND j.is_open = 1"
        rows = self.db.fetch_all(sql + " ORDER BY j.created_at DESC", (category, f"%{location}%"))
        return [JobPosting.from_row(r) for r in rows]

    def list_all(self) -> List[JobPosting]:
        return [JobPosting.from_row(r) for r in self.db.fetch_all(_SELECT + " ORDER BY j.created_at DESC")]

    def list_by_poster(self, user_id: int) -> List[JobPosting]:
        rows = self.db.fetch_all(_SELECT + " WHERE j.posted_by = ? ORDER BY j.created_at DESC", (user_id,))
        return [JobPosting.from_row(r) for r in rows]

    def update(self, job_id: int, title: str, description: str, talent_path_id: int,
               location: str, contact: str, how_to_apply: str, is_open: bool) -> bool:
        cur = self.db.execute(
            """UPDATE job_postings SET title = ?, description = ?, talent_path_id = ?,
                   location = ?, contact = ?, how_to_apply = ?, is_open = ?
               WHERE id = ?""",
            (title, description, talent_path_id, location, contact, how_to_apply,
             int(is_open), job_id),
        )
        return cur.rowcount > 0

    def delete(self, job_id: int) -> bool:
        return self.db.execute("DELETE FROM job_postings WHERE id = ?", (job_id,)).rowcount > 0

    def count_open(self) -> int:
        return self.db.scalar("SELECT COUNT(*) FROM job_postings WHERE is_open = 1")
