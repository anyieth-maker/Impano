"""Sign-up, log-in and profile updates."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Optional

from impano.models import User
from impano.repositories import TalentPathRepository, UserRepository
from . import validators as v
from .errors import AuthenticationError, NotFoundError, ValidationError


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Return (hash, salt). Passwords are never stored in plain text."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return digest.hex(), salt


class AuthService:
    def __init__(self, users: UserRepository, talent_paths: TalentPathRepository) -> None:
        self.users = users
        self.talent_paths = talent_paths

    def register(self, full_name: str, username: str, password: str, phone: str,
                 location: str, talent_path_id: Optional[int] = None,
                 role: str = "member", bio: str = "") -> User:
        full_name = v.require_text(full_name, "Full name", 80)
        username = v.validate_username(username)
        v.validate_password(password)
        phone = v.validate_phone(phone)
        location = v.require_text(location, "Location", 80)
        role = v.validate_role(role)
        if self.users.username_exists(username):
            raise ValidationError(f"The username '{username}' is already taken.")
        if talent_path_id is not None and not self.talent_paths.get(talent_path_id):
            raise NotFoundError("That talent path does not exist.")

        password_hash, salt = hash_password(password)
        user_id = self.users.create(full_name, username, password_hash, salt, phone,
                                    location, talent_path_id, role, bio.strip())
        return self.users.get(user_id)

    def login(self, username: str, password: str) -> User:
        creds = self.users.get_credentials((username or "").strip())
        if creds:
            user_id, stored_hash, salt = creds
            attempt, _ = hash_password(password or "", salt)
            if hmac.compare_digest(attempt, stored_hash):
                return self.users.get(user_id)
        raise AuthenticationError("Incorrect username or password.")

    def update_profile(self, user: User, full_name: str, phone: str, location: str,
                       talent_path_id: Optional[int], bio: str) -> User:
        full_name = v.require_text(full_name, "Full name", 80)
        phone = v.validate_phone(phone)
        location = v.require_text(location, "Location", 80)
        if talent_path_id is not None and not self.talent_paths.get(talent_path_id):
            raise NotFoundError("That talent path does not exist.")
        self.users.update_profile(user.id, full_name, phone, location, talent_path_id, bio.strip())
        return self.users.get(user.id)
