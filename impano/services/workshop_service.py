"""Feature 2 (workshop registration) + workshop management for mentors/admins."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from impano.models import Registration, User, Workshop
from impano.repositories import TalentPathRepository, WorkshopRepository
from . import validators as v
from .errors import NotFoundError, PermissionDeniedError, ValidationError


class WorkshopService:
    def __init__(self, workshops: WorkshopRepository, talent_paths: TalentPathRepository) -> None:
        self.workshops = workshops
        self.talent_paths = talent_paths

    # ---------------------------------------------------------- browsing
    def upcoming(self) -> List[Workshop]:
        return self.workshops.list_upcoming(date.today().isoformat())

    def get(self, workshop_id: int) -> Workshop:
        workshop = self.workshops.get(workshop_id)
        if not workshop:
            raise NotFoundError(f"No workshop with ID {workshop_id}.")
        return workshop

    # ------------------------------------------------------ registration
    def register(self, user: User, workshop_id: int, attendee_name: str, phone: str) -> Workshop:
        """Verify the ID, check for space, then save the registration."""
        workshop = self.get(workshop_id)
        if workshop.event_date < date.today().isoformat():
            raise ValidationError("This workshop has already taken place.")
        if self.workshops.is_registered(workshop_id, user.id):
            raise ValidationError("You are already registered for this workshop.")
        if workshop.is_full:
            raise ValidationError("Sorry, this workshop is full.")
        name = v.require_text(attendee_name, "Attendee name", 80)
        phone = v.validate_phone(phone)
        self.workshops.register(workshop_id, user.id, name, phone)
        return self.get(workshop_id)

    def my_registrations(self, user: User) -> List[Registration]:
        return self.workshops.registrations_for_user(user.id)

    def cancel(self, user: User, workshop_id: int) -> None:
        if not self.workshops.cancel(workshop_id, user.id):
            raise NotFoundError("You are not registered for that workshop.")

    # -------------------------------------------- management (mentor/admin)
    def _check_can_manage(self, user: User, workshop: Optional[Workshop] = None) -> None:
        if user.is_admin:
            return
        if not user.is_mentor:
            raise PermissionDeniedError("Only mentors and admins can manage workshops.")
        if workshop is not None and workshop.host_id != user.id:
            raise PermissionDeniedError("You can only manage workshops that you host.")

    def _clean(self, title, description, talent_path_id, location, event_date, capacity):
        if talent_path_id is not None and not self.talent_paths.get(talent_path_id):
            raise NotFoundError("That talent path does not exist.")
        return (
            v.require_text(title, "Title", 100),
            (description or "").strip(),
            talent_path_id,
            v.require_text(location, "Location", 80),
            v.validate_date(event_date),
            v.validate_positive_int(capacity, "Capacity"),
        )

    def hosted_by(self, user: User) -> List[Workshop]:
        return self.workshops.list_all() if user.is_admin else self.workshops.list_by_host(user.id)

    def create(self, user: User, title: str, description: str, talent_path_id: Optional[int],
               location: str, event_date: str, capacity) -> Workshop:
        self._check_can_manage(user)
        data = self._clean(title, description, talent_path_id, location, event_date, capacity)
        return self.get(self.workshops.create(*data, host_id=user.id))

    def update(self, user: User, workshop_id: int, title: str, description: str,
               talent_path_id: Optional[int], location: str, event_date: str,
               capacity) -> Workshop:
        workshop = self.get(workshop_id)
        self._check_can_manage(user, workshop)
        data = self._clean(title, description, talent_path_id, location, event_date, capacity)
        if data[-1] < workshop.registered:
            raise ValidationError(
                f"Capacity cannot be lower than the {workshop.registered} people already registered."
            )
        self.workshops.update(workshop_id, *data)
        return self.get(workshop_id)

    def delete(self, user: User, workshop_id: int) -> None:
        self._check_can_manage(user, self.get(workshop_id))
        self.workshops.delete(workshop_id)

    def attendees(self, user: User, workshop_id: int) -> List[Registration]:
        self._check_can_manage(user, self.get(workshop_id))
        return self.workshops.attendees(workshop_id)
