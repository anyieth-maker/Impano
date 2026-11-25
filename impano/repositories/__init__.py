"""Repositories: the only place that writes SQL queries for each table."""

from .job_repository import JobRepository
from .mentorship_repository import MentorshipRepository
from .program_repository import ProgramRepository
from .talent_path_repository import TalentPathRepository
from .user_repository import UserRepository
from .workshop_repository import WorkshopRepository

__all__ = [
    "JobRepository",
    "MentorshipRepository",
    "ProgramRepository",
    "TalentPathRepository",
    "UserRepository",
    "WorkshopRepository",
]
