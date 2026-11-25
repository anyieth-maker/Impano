"""SQL for the training_programs and favorites tables."""

from __future__ import annotations

from typing import List, Optional

from impano.database import Database
from impano.models import TrainingProgram

_SELECT = """
    SELECT p.*, tp.name AS talent_path, tp.category AS category
    FROM training_programs p
    JOIN talent_paths tp ON tp.id = p.talent_path_id
"""


class ProgramRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    # ------------------------------------------------------------- CRUD
    def create(self, name: str, description: str, talent_path_id: int,
               center_name: str, location: str, contact: str) -> int:
        return self.db.insert(
            """INSERT INTO training_programs
                   (name, description, talent_path_id, center_name, location, contact)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, description, talent_path_id, center_name, location, contact),
        )

    def get(self, program_id: int) -> Optional[TrainingProgram]:
        row = self.db.fetch_one(_SELECT + " WHERE p.id = ?", (program_id,))
        return TrainingProgram.from_row(row) if row else None

    def list_all(self) -> List[TrainingProgram]:
        rows = self.db.fetch_all(_SELECT + " ORDER BY tp.name, p.name")
        return [TrainingProgram.from_row(r) for r in rows]

    def search(self, talent_keyword: str, location: str = "") -> List[TrainingProgram]:
        """Feature 1: match on talent path OR program name, optionally by location."""
        like = f"%{talent_keyword}%"
        rows = self.db.fetch_all(
            _SELECT + """ WHERE (tp.name LIKE ? OR p.name LIKE ? OR tp.category LIKE ?)
                          AND p.location LIKE ?
                          ORDER BY p.location, p.name""",
            (like, like, like, f"%{location}%"),
        )
        return [TrainingProgram.from_row(r) for r in rows]

    def update(self, program_id: int, name: str, description: str, talent_path_id: int,
               center_name: str, location: str, contact: str) -> bool:
        cur = self.db.execute(
            """UPDATE training_programs
               SET name = ?, description = ?, talent_path_id = ?,
                   center_name = ?, location = ?, contact = ?
               WHERE id = ?""",
            (name, description, talent_path_id, center_name, location, contact, program_id),
        )
        return cur.rowcount > 0

    def delete(self, program_id: int) -> bool:
        return self.db.execute("DELETE FROM training_programs WHERE id = ?", (program_id,)).rowcount > 0

    # -------------------------------------------------------- favorites
    def add_favorite(self, user_id: int, program_id: int) -> None:
        self.db.execute(
            "INSERT OR IGNORE INTO favorites (user_id, program_id) VALUES (?, ?)",
            (user_id, program_id),
        )

    def remove_favorite(self, user_id: int, program_id: int) -> bool:
        cur = self.db.execute(
            "DELETE FROM favorites WHERE user_id = ? AND program_id = ?", (user_id, program_id)
        )
        return cur.rowcount > 0

    def is_favorite(self, user_id: int, program_id: int) -> bool:
        return bool(self.db.scalar(
            "SELECT 1 FROM favorites WHERE user_id = ? AND program_id = ?", (user_id, program_id)
        ))

    def list_favorites(self, user_id: int) -> List[TrainingProgram]:
        rows = self.db.fetch_all(
            _SELECT + """ JOIN favorites f ON f.program_id = p.id
                          WHERE f.user_id = ? ORDER BY f.saved_at DESC""",
            (user_id,),
        )
        return [TrainingProgram.from_row(r) for r in rows]

    def count(self) -> int:
        return self.db.scalar("SELECT COUNT(*) FROM training_programs")
