"""Feature 1 (search training programs) + bonus favorites + admin CRUD."""

from __future__ import annotations

from typing import List

from impano.models import TrainingProgram, User
from impano.repositories import ProgramRepository, TalentPathRepository
from . import validators as v
from .errors import NotFoundError, PermissionDeniedError


class ProgramService:
    def __init__(self, programs: ProgramRepository, talent_paths: TalentPathRepository) -> None:
        self.programs = programs
        self.talent_paths = talent_paths

    # ---------------------------------------------------------- everyone
    def search(self, talent_keyword: str, location: str = "") -> List[TrainingProgram]:
        keyword = v.require_text(talent_keyword, "Talent path", 50)
        return self.programs.search(keyword, (location or "").strip())

    def get(self, program_id: int) -> TrainingProgram:
        program = self.programs.get(program_id)
        if not program:
            raise NotFoundError(f"No training program with ID {program_id}.")
        return program

    def list_all(self) -> List[TrainingProgram]:
        return self.programs.list_all()

    # --------------------------------------------------- favorites (bonus)
    def save_favorite(self, user: User, program_id: int) -> TrainingProgram:
        program = self.get(program_id)
        self.programs.add_favorite(user.id, program.id)
        return program

    def remove_favorite(self, user: User, program_id: int) -> None:
        if not self.programs.remove_favorite(user.id, program_id):
            raise NotFoundError("That program is not in your favorites.")

    def favorites(self, user: User) -> List[TrainingProgram]:
        return self.programs.list_favorites(user.id)

    # ------------------------------------------------------- admin CRUD
    def _check_admin(self, user: User) -> None:
        if not user.is_admin:
            raise PermissionDeniedError("Only admins can manage training programs.")

    def _clean(self, name, description, talent_path_id, center_name, location, contact):
        if not self.talent_paths.get(talent_path_id):
            raise NotFoundError("That talent path does not exist.")
        return (
            v.require_text(name, "Program name", 100),
            (description or "").strip(),
            talent_path_id,
            v.require_text(center_name, "Center name", 100),
            v.require_text(location, "Location", 80),
            v.require_text(contact, "Contact", 100),
        )

    def create(self, user: User, name: str, description: str, talent_path_id: int,
               center_name: str, location: str, contact: str) -> TrainingProgram:
        self._check_admin(user)
        program_id = self.programs.create(*self._clean(name, description, talent_path_id,
                                                       center_name, location, contact))
        return self.get(program_id)

    def update(self, user: User, program_id: int, name: str, description: str,
               talent_path_id: int, center_name: str, location: str,
               contact: str) -> TrainingProgram:
        self._check_admin(user)
        self.get(program_id)
        self.programs.update(program_id, *self._clean(name, description, talent_path_id,
                                                      center_name, location, contact))
        return self.get(program_id)

    def delete(self, user: User, program_id: int) -> None:
        self._check_admin(user)
        if not self.programs.delete(program_id):
            raise NotFoundError(f"No training program with ID {program_id}.")
