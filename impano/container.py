"""Wires the layers together: Database -> Repositories -> Services.

Python code -> SQL flow:
    CLI menu  ->  Service (rules)  ->  Repository (SQL)  ->  Database (sqlite3)
"""

from __future__ import annotations

from impano.database import Database
from impano.database.seed import seed_if_empty
from impano.repositories import (JobRepository, MentorshipRepository, ProgramRepository,
                                 TalentPathRepository, UserRepository, WorkshopRepository)
from impano.services import (AdminService, AuthService, JobService, MentorshipService,
                             ProgramService, WorkshopService)


class Container:
    def __init__(self, db_path=None, seed: bool = True) -> None:
        self.db = Database(db_path) if db_path else Database()
        self.db.init_schema()

        # Repositories (SQL)
        talent_paths = TalentPathRepository(self.db)
        users = UserRepository(self.db)
        programs = ProgramRepository(self.db)
        workshops = WorkshopRepository(self.db)
        jobs = JobRepository(self.db)
        mentorship = MentorshipRepository(self.db)

        # Services (rules)
        self.auth = AuthService(users, talent_paths)
        self.programs = ProgramService(programs, talent_paths)
        self.workshops = WorkshopService(workshops, talent_paths)
        self.jobs = JobService(jobs, talent_paths)
        self.mentorship = MentorshipService(mentorship, users)
        self.admin = AdminService(users, talent_paths, programs, workshops, jobs)

        if seed:
            seed_if_empty(self)

    def close(self) -> None:
        self.db.close()
