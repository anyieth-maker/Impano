"""Feature 3 (discover job opportunities) + posting jobs for mentors/admins."""

from __future__ import annotations

from typing import List

from impano.models import JobPosting, User
from impano.repositories import JobRepository, TalentPathRepository
from . import validators as v
from .errors import NotFoundError, PermissionDeniedError


class JobService:
    def __init__(self, jobs: JobRepository, talent_paths: TalentPathRepository) -> None:
        self.jobs = jobs
        self.talent_paths = talent_paths

    def discover(self, category: str, location: str = "") -> List[JobPosting]:
        return self.jobs.search_by_category(v.validate_category(category), (location or "").strip())

    def get(self, job_id: int) -> JobPosting:
        job = self.jobs.get(job_id)
        if not job:
            raise NotFoundError(f"No job posting with ID {job_id}.")
        return job

    # ------------------------------------------------------ management
    def _check_can_manage(self, user: User, job: JobPosting = None) -> None:
        if user.is_admin:
            return
        if not user.is_mentor:
            raise PermissionDeniedError("Only mentors and admins can post jobs.")
        if job is not None and job.posted_by != user.id:
            raise PermissionDeniedError("You can only change jobs that you posted.")

    def _clean(self, title, description, talent_path_id, location, contact, how_to_apply):
        if not self.talent_paths.get(talent_path_id):
            raise NotFoundError("That talent path does not exist.")
        return (
            v.require_text(title, "Title", 100),
            (description or "").strip(),
            talent_path_id,
            v.require_text(location, "Location", 80),
            v.require_text(contact, "Contact", 100),
            v.require_text(how_to_apply, "How to apply", 200),
        )

    def managed_by(self, user: User) -> List[JobPosting]:
        return self.jobs.list_all() if user.is_admin else self.jobs.list_by_poster(user.id)

    def create(self, user: User, title: str, description: str, talent_path_id: int,
               location: str, contact: str, how_to_apply: str) -> JobPosting:
        self._check_can_manage(user)
        data = self._clean(title, description, talent_path_id, location, contact, how_to_apply)
        return self.get(self.jobs.create(*data, posted_by=user.id))

    def update(self, user: User, job_id: int, title: str, description: str,
               talent_path_id: int, location: str, contact: str, how_to_apply: str,
               is_open: bool) -> JobPosting:
        self._check_can_manage(user, self.get(job_id))
        data = self._clean(title, description, talent_path_id, location, contact, how_to_apply)
        self.jobs.update(job_id, *data, is_open=is_open)
        return self.get(job_id)

    def delete(self, user: User, job_id: int) -> None:
        self._check_can_manage(user, self.get(job_id))
        self.jobs.delete(job_id)
