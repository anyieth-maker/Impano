"""SQL for the users table."""

from __future__ import annotations

from typing import List, Optional, Tuple

from impano.database import Database
from impano.models import User

_SELECT = """
    SELECT u.*, tp.name AS talent_path
    FROM users u
    LEFT JOIN talent_paths tp ON tp.id = u.talent_path_id
"""


class UserRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, full_name: str, username: str, password_hash: str, salt: str,
               phone: str, location: str, talent_path_id: Optional[int],
               role: str = "member", bio: str = "") -> int:
        return self.db.insert(
            """INSERT INTO users (full_name, username, password_hash, salt, phone,
                                  location, talent_path_id, role, bio)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (full_name, username, password_hash, salt, phone, location,
             talent_path_id, role, bio),
        )

    def get(self, user_id: int) -> Optional[User]:
        row = self.db.fetch_one(_SELECT + " WHERE u.id = ?", (user_id,))
        return User.from_row(row) if row else None

    def get_credentials(self, username: str) -> Optional[Tuple[int, str, str]]:
        """Return (id, password_hash, salt) for login checks."""
        row = self.db.fetch_one(
            "SELECT id, password_hash, salt FROM users WHERE username = ?", (username,)
        )
        return (row["id"], row["password_hash"], row["salt"]) if row else None

    def username_exists(self, username: str) -> bool:
        return bool(self.db.scalar("SELECT 1 FROM users WHERE username = ?", (username,)))

    def list_all(self) -> List[User]:
        return [User.from_row(r) for r in self.db.fetch_all(_SELECT + " ORDER BY u.role, u.full_name")]

    def list_mentors(self, talent_keyword: str = "", location: str = "") -> List[User]:
        rows = self.db.fetch_all(
            _SELECT + """ WHERE u.role = 'mentor'
                          AND COALESCE(tp.name, '') LIKE ?
                          AND u.location LIKE ?
                          ORDER BY u.full_name""",
            (f"%{talent_keyword}%", f"%{location}%"),
        )
        return [User.from_row(r) for r in rows]

    def update_profile(self, user_id: int, full_name: str, phone: str, location: str,
                       talent_path_id: Optional[int], bio: str) -> bool:
        cur = self.db.execute(
            """UPDATE users SET full_name = ?, phone = ?, location = ?,
                                talent_path_id = ?, bio = ?
               WHERE id = ?""",
            (full_name, phone, location, talent_path_id, bio, user_id),
        )
        return cur.rowcount > 0

    def update_role(self, user_id: int, role: str) -> bool:
        return self.db.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id)).rowcount > 0

    def delete(self, user_id: int) -> bool:
        return self.db.execute("DELETE FROM users WHERE id = ?", (user_id,)).rowcount > 0

    def count_by_role(self) -> dict:
        rows = self.db.fetch_all("SELECT role, COUNT(*) AS n FROM users GROUP BY role")
        return {r["role"]: r["n"] for r in rows}
