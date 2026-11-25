"""Admin-only operations: users, talent paths and platform statistics."""

from __future__ import annotations

from typing import Dict, List

from impano.models import TalentPath, User
from impano.repositories import (JobRepository, ProgramRepository, TalentPathRepository,
                                 UserRepository, WorkshopRepository)
from . import validators as v
from .errors import NotFoundError, PermissionDeniedError, ValidationError


class AdminService:
    def __init__(self, users: UserRepository, talent_paths: TalentPathRepository,
                 programs: ProgramRepository, workshops: WorkshopRepository,
                 jobs: JobRepository) -> None:
        self.users = users
        self.talent_paths = talent_paths
        self.programs = programs
        self.workshops = workshops
        self.jobs = jobs

    @staticmethod
    def _check_admin(user: User) -> None:
        if not user.is_admin:
            raise PermissionDeniedError("Admin access required.")

    # --------------------------------------------------------- users
    def list_users(self, admin: User) -> List[User]:
        self._check_admin(admin)
        return self.users.list_all()

    def change_role(self, admin: User, user_id: int, role: str) -> User:
        self._check_admin(admin)
        role = v.validate_role(role)
        if user_id == admin.id:
            raise ValidationError("You cannot change your own role.")
        if not self.users.update_role(user_id, role):
            raise NotFoundError(f"No user with ID {user_id}.")
        return self.users.get(user_id)

    def delete_user(self, admin: User, user_id: int) -> None:
        self._check_admin(admin)
        if user_id == admin.id:
            raise ValidationError("You cannot delete your own account while logged in.")
        if not self.users.delete(user_id):
            raise NotFoundError(f"No user with ID {user_id}.")

    # -------------------------------------------------- talent paths
    def list_talent_paths(self) -> List[TalentPath]:
        return self.talent_paths.list_all()

    def get_talent_path(self, path_id: int) -> TalentPath:
        path = self.talent_paths.get(path_id)
        if not path:
            raise NotFoundError(f"No talent path with ID {path_id}.")
        return path

    def create_talent_path(self, admin: User, name: str, category: str) -> TalentPath:
        self._check_admin(admin)
        name = v.require_text(name, "Talent path name", 50).title()
        category = v.validate_category(category)
        if self.talent_paths.get_by_name(name):
            raise ValidationError(f"Talent path '{name}' already exists.")
        return self.talent_paths.get(self.talent_paths.create(name, category))

    def update_talent_path(self, admin: User, path_id: int, name: str, category: str) -> TalentPath:
        self._check_admin(admin)
        self.get_talent_path(path_id)
        name = v.require_text(name, "Talent path name", 50).title()
        existing = self.talent_paths.get_by_name(name)
        if existing and existing.id != path_id:
            raise ValidationError(f"Talent path '{name}' already exists.")
        self.talent_paths.update(path_id, name, v.validate_category(category))
        return self.talent_paths.get(path_id)

    def delete_talent_path(self, admin: User, path_id: int) -> None:
        self._check_admin(admin)
        if not self.talent_paths.delete(path_id):
            raise NotFoundError(f"No talent path with ID {path_id}.")

    # -------------------------------------------------------- stats
    def statistics(self, admin: User) -> Dict[str, int]:
        self._check_admin(admin)
        roles = self.users.count_by_role()
        return {
            "Members": roles.get("member", 0),
            "Mentors": roles.get("mentor", 0),
            "Admins": roles.get("admin", 0),
            "Talent paths": len(self.talent_paths.list_all()),
            "Training programs": self.programs.count(),
            "Workshops": len(self.workshops.list_all()),
            "Workshop registrations": self.workshops.count_registrations(),
            "Open job postings": self.jobs.count_open(),
        }
