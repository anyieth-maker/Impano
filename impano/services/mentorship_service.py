"""Connecting members with mentors."""

from __future__ import annotations

from typing import List

from impano.models import MentorshipRequest, User
from impano.repositories import MentorshipRepository, UserRepository
from . import validators as v
from .errors import NotFoundError, PermissionDeniedError, ValidationError


class MentorshipService:
    def __init__(self, requests: MentorshipRepository, users: UserRepository) -> None:
        self.requests = requests
        self.users = users

    def find_mentors(self, talent_keyword: str = "", location: str = "") -> List[User]:
        return self.users.list_mentors((talent_keyword or "").strip(), (location or "").strip())

    def request(self, member: User, mentor_id: int, message: str) -> MentorshipRequest:
        mentor = self.users.get(mentor_id)
        if not mentor or not mentor.is_mentor:
            raise NotFoundError(f"No mentor with ID {mentor_id}.")
        if mentor.id == member.id:
            raise ValidationError("You cannot send a mentorship request to yourself.")
        if self.requests.has_pending(member.id, mentor_id):
            raise ValidationError("You already have a pending request with this mentor.")
        message = v.require_text(message, "Message", 300)
        return self.requests.get(self.requests.create(member.id, mentor_id, message))

    def sent_by(self, member: User) -> List[MentorshipRequest]:
        return self.requests.list_for_member(member.id)

    def received_by(self, mentor: User) -> List[MentorshipRequest]:
        if not mentor.is_mentor:
            raise PermissionDeniedError("Only mentors receive mentorship requests.")
        return self.requests.list_for_mentor(mentor.id)

    def respond(self, mentor: User, request_id: int, accept: bool) -> MentorshipRequest:
        req = self.requests.get(request_id)
        if not req or req.mentor_id != mentor.id:
            raise NotFoundError(f"No request with ID {request_id} in your inbox.")
        if req.status != "pending":
            raise ValidationError(f"This request was already {req.status}.")
        self.requests.update_status(request_id, "accepted" if accept else "declined")
        return self.requests.get(request_id)
