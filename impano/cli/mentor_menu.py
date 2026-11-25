"""Menu for mentors: answer requests, host workshops, post opportunities."""

from __future__ import annotations

from impano.container import Container
from impano.models import User
from impano.services.validators import validate_date
from . import shared, ui


class MentorMenu:
    def __init__(self, app: Container, user: User) -> None:
        self.app = app
        self.user = user

    def run(self) -> None:
        ui.run_menu(
            f"MENTOR MENU - {self.user.full_name}",
            {
                "1": ("Mentorship requests inbox", self.inbox),
                "2": ("Host a new workshop", self.create_workshop),
                "3": ("Manage my workshops & view attendees", self.manage_workshops),
                "4": ("Post a job / business opportunity", self.post_job),
                "5": ("Manage my job postings", self.manage_jobs),
                "6": ("Search training programs", lambda: shared.search_programs(self.app)),
                "7": ("View / edit my profile", self.profile),
            },
            exit_label="Log out",
        )

    # --------------------------------------------------------- requests
    def inbox(self):
        ui.subheader("Mentorship requests")
        reqs = self.app.mentorship.received_by(self.user)
        if not reqs:
            ui.info("No mentorship requests yet.")
            return
        for r in reqs:
            print(f"\n  [{r.id}] {r.member_name} ({r.member_phone}) - {r.status.upper()}")
            print(ui.wrap(f'"{r.message}"', "      "))
        if any(r.status == "pending" for r in reqs) and ui.confirm("\nRespond to a request?"):
            req_id = ui.ask_int("Request ID")
            accept = ui.confirm("Accept this request?")
            req = self.app.mentorship.respond(self.user, req_id, accept)
            ui.success(f"Request {req.status}. "
                       + (f"Contact {req.member_name} on {req.member_phone}." if accept else ""))

    # -------------------------------------------------------- workshops
    def create_workshop(self):
        ui.subheader("Host a new workshop")
        title = ui.ask("Title")
        description = ui.ask("Description", required=False)
        path_id = shared.pick_talent_path(self.app, required=False)
        location = ui.ask("Location / venue")
        event_date = ui.ask_valid("Date (YYYY-MM-DD)", validate_date)
        capacity = ui.ask_int("Capacity (max attendees)")
        w = self.app.workshops.create(self.user, title, description, path_id,
                                      location, event_date, capacity)
        ui.success(f"Workshop '{w.title}' created with ID {w.id}.")

    def manage_workshops(self):
        manage_workshops(self.app, self.user)

    # ------------------------------------------------------------- jobs
    def post_job(self):
        ui.subheader("Post a job / business opportunity")
        title = ui.ask("Job title")
        description = ui.ask("Description", required=False)
        path_id = shared.pick_talent_path(self.app)
        location = ui.ask("Location")
        contact = ui.ask("Contact (phone or email)", default=self.user.phone)
        how = ui.ask("How to apply")
        job = self.app.jobs.create(self.user, title, description, path_id, location, contact, how)
        ui.success(f"Job '{job.title}' posted with ID {job.id}.")

    def manage_jobs(self):
        manage_jobs(self.app, self.user)

    def profile(self):
        self.user = shared.edit_profile(self.app, self.user)


# ---------------------------------------------------------------------------
# Shared with the admin menu (admins can manage every record, mentors only theirs)
# ---------------------------------------------------------------------------
def manage_workshops(app: Container, user: User) -> None:
    ui.subheader("Workshops")
    workshops = app.workshops.hosted_by(user)
    shared.show_workshops(workshops)
    if not workshops:
        return
    print("\n  1. View attendees   2. Edit   3. Delete   0. Back")
    action = ui.ask("Action", default="0")
    if action == "0":
        return
    workshop_id = ui.ask_int("Workshop ID")
    if action == "1":
        attendees = app.workshops.attendees(user, workshop_id)
        ui.table(["Name", "Phone", "Registered at"],
                 [(a.attendee_name, a.phone, a.registered_at) for a in attendees],
                 empty="No one has registered yet.")
    elif action == "2":
        w = app.workshops.get(workshop_id)
        ui.info("Press Enter to keep the current value.")
        title = ui.ask("Title", default=w.title)
        description = ui.ask("Description", required=False, default=w.description)
        path_id = shared.pick_talent_path(app, required=False, current=w.talent_path_id)
        location = ui.ask("Location", default=w.location)
        event_date = ui.ask_valid("Date (YYYY-MM-DD)", validate_date, default=w.event_date)
        capacity = ui.ask_int("Capacity", default=w.capacity)
        app.workshops.update(user, workshop_id, title, description, path_id,
                             location, event_date, capacity)
        ui.success("Workshop updated.")
    elif action == "3":
        if ui.confirm("Delete this workshop and all its registrations?"):
            app.workshops.delete(user, workshop_id)
            ui.success("Workshop deleted.")
    else:
        ui.error("Unknown action.")


def manage_jobs(app: Container, user: User) -> None:
    ui.subheader("Job postings")
    jobs = app.jobs.managed_by(user)
    if not jobs:
        ui.info("No job postings yet.")
        return
    shared.show_jobs(jobs, show_status=True)
    print("\n  1. Edit   2. Open/close   3. Delete   0. Back")
    action = ui.ask("Action", default="0")
    if action == "0":
        return
    job_id = ui.ask_int("Job ID")
    job = app.jobs.get(job_id)
    if action == "1":
        ui.info("Press Enter to keep the current value.")
        title = ui.ask("Title", default=job.title)
        description = ui.ask("Description", required=False, default=job.description)
        path_id = shared.pick_talent_path(app, current=job.talent_path_id)
        location = ui.ask("Location", default=job.location)
        contact = ui.ask("Contact", default=job.contact)
        how = ui.ask("How to apply", default=job.how_to_apply)
        app.jobs.update(user, job_id, title, description, path_id, location,
                        contact, how, job.is_open)
        ui.success("Job updated.")
    elif action == "2":
        app.jobs.update(user, job_id, job.title, job.description, job.talent_path_id,
                        job.location, job.contact, job.how_to_apply, not job.is_open)
        ui.success(f"Job is now {'CLOSED' if job.is_open else 'OPEN'}.")
    elif action == "3":
        if ui.confirm(f"Delete '{job.title}'?"):
            app.jobs.delete(user, job_id)
            ui.success("Job deleted.")
    else:
        ui.error("Unknown action.")
