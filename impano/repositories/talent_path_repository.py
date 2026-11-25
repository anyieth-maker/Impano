"""SQL for the talent_paths table."""

from __future__ import annotations

from typing import List, Optional

from impano.database import Database
from impano.models import TalentPath


class TalentPathRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, name: str, category: str) -> int:
        return self.db.insert(
            "INSERT INTO talent_paths (name, category) VALUES (?, ?)", (name, category)
        )

    def get(self, path_id: int) -> Optional[TalentPath]:
        row = self.db.fetch_one("SELECT * FROM talent_paths WHERE id = ?", (path_id,))
        return TalentPath.from_row(row) if row else None

    def get_by_name(self, name: str) -> Optional[TalentPath]:
        row = self.db.fetch_one("SELECT * FROM talent_paths WHERE name = ?", (name,))
        return TalentPath.from_row(row) if row else None

    def list_all(self) -> List[TalentPath]:
        rows = self.db.fetch_all("SELECT * FROM talent_paths ORDER BY category, name")
        return [TalentPath.from_row(r) for r in rows]

    def update(self, path_id: int, name: str, category: str) -> bool:
        cur = self.db.execute(
            "UPDATE talent_paths SET name = ?, category = ? WHERE id = ?",
            (name, category, path_id),
        )
        return cur.rowcount > 0

    def delete(self, path_id: int) -> bool:
        return self.db.execute("DELETE FROM talent_paths WHERE id = ?", (path_id,)).rowcount > 0
