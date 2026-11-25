"""Screens used by more than one role (the three core features + pickers)."""

from __future__ import annotations

from typing import List, Optional

from impano.container import Container
from impano.models import CATEGORIES, JobPosting, TrainingProgram, User, Workshop
from impano.services.validators import validate_phone
from . import ui


# ------------------------------------------------------------- pickers
def pick_talent_path(app: Container, required: bool = True,
                     current: Optional[int] = None) -> Optional[int]:
    paths = app.admin.list_talent_paths()
    ui.table(["ID", "Talent path", "Category"], [(p.id, p.name, p.category) for p in paths])
    prompt = "Talent path ID" + ("" if required else " (Enter to skip)")
    return ui.ask_int(prompt, required=required, default=current)


def pick_category() -> str:
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat}")
    while True:
        n = ui.ask_int(f"Pick a skill category (1-{len(CATEGORIES)})")
        if 1 <= n <= len(CATEGORIES):
            return CATEGORIES[n - 1]
        ui.error("Invalid category number.")


# ------------------------------------------------------------- printers
def show_programs(programs: List[TrainingProgram]) -> None:
    for p in programs:
        print(f"\n  [{p.id}] {p.name}  ({p.talent_path} - {p.category})")
        print(f"      Center  : {p.center_name}, {p.location}")
        print(f"      Contact : {p.contact}")
        if p.description:
            print(ui.wrap(p.description, "      "))


def show_workshops(workshops: List[Workshop]) -> None:
    ui.table(
        ["ID", "Title", "Date", "Location", "Seats left"],
        [(w.id, w.title, w.event_date, w.location,
          "FULL" if w.is_full else f"{w.seats_left}/{w.capacity}") for w in workshops],
        empty="No upcoming workshops.",
    )


def show_jobs(jobs: List[JobPosting], show_status: bool = False) -> None:
    for j in jobs:
        status = "" if not show_status else ("  [OPEN]" if j.is_open else "  [CLOSED]")
        print(f"\n  [{j.id}] {j.title}  ({j.talent_path}, {j.location}){status}")
        if j.description:
            print(ui.wrap(j.description, "      "))
        print(f"      Contact      : {j.contact}")
        print(f"      How to apply : {j.how_to_apply}")


def show_mentors(mentors: List[User]) -> None:
    for m in mentors:
        print(f"\n  [{m.id}] {m.full_name}  ({m.talent_path or 'General'}, {m.location})")
        if m.bio:
            print(ui.wrap(m.bio, "      "))


# ------------------------------------------------------------- features
def search_programs(app: Container, user: Optional[User] = None) -> None:
    """Feature 1: Search programs by talent path."""
    ui.subheader("Search talent paths & training centers")
    keyword = ui.ask("Please enter your talent path (e.g., Carpentry, Music, Sports)")
    location = ui.ask("Your location (Enter for anywhere)", required=False)
    results = app.programs.search(keyword, location)
    if not results:
        ui.info(f"No training programs found for '{keyword}'. Try another talent path.")
        return
    show_programs(results)
    ui.success("Here are the nearby training centers and program locations for your field!")
    if user and ui.confirm("\nSave one of these to your favorites?"):
        program = app.programs.save_favorite(user, ui.ask_int("Program ID"))
        ui.success(f"'{program.name}' saved to your favorites.")


def register_workshop(app: Container, user: User) -> None:
    """Feature 2: Register for an awareness workshop."""
    ui.subheader("Register for awareness workshops")
    workshops = app.workshops.upcoming()
    show_workshops(workshops)
    if not workshops:
        return
    workshop_id = ui.ask_int("\nWorkshop ID")
    workshop = app.workshops.get(workshop_id)
    print(f"\n  {workshop.title} - {workshop.event_date} @ {workshop.location}")
    if workshop.description:
        print(ui.wrap(workshop.description))
    name = ui.ask("Your name", default=user.full_name)
    phone = ui.ask_valid("Phone number", validate_phone, default=user.phone)
    app.workshops.register(user, workshop_id, name, phone)
    ui.success("Registration successful! Further workshop details will be sent "
               "to your phone number via message.")


def discover_jobs(app: Container) -> None:
    """Feature 3: Discover job and business opportunities."""
    ui.subheader("Discover job and business opportunities")
    category = pick_category()
    location = ui.ask("Location (Enter for anywhere)", required=False)
    jobs = app.jobs.discover(category, location)
    if not jobs:
        ui.info(f"No open {category} opportunities right now. Check back soon!")
        return
    show_jobs(jobs)
    ui.success(f"{len(jobs)} open {category} opportunit{'y' if len(jobs) == 1 else 'ies'} found.")


def view_profile(user: User) -> None:
    ui.subheader("My profile")
    print(f"  Name        : {user.full_name}")
    print(f"  Username    : {user.username}")
    print(f"  Role        : {user.role}")
    print(f"  Phone       : {user.phone}")
    print(f"  Location    : {user.location}")
    print(f"  Talent path : {user.talent_path or '-'}")
    if user.bio:
        print(f"  Bio         : {user.bio}")


def edit_profile(app: Container, user: User) -> User:
    """Update the logged-in user's own profile. Enter keeps the current value."""
    view_profile(user)
    ui.subheader("Edit profile (press Enter to keep the current value)")
    name = ui.ask("Full name", default=user.full_name)
    phone = ui.ask_valid("Phone", validate_phone, default=user.phone)
    location = ui.ask("Location", default=user.location)
    path_id = pick_talent_path(app, required=False, current=user.talent_path_id)
    bio = ui.ask("Short bio", required=False, default=user.bio)
    updated = app.auth.update_profile(user, name, phone, location, path_id, bio)
    ui.success("Profile updated.")
    return updated


def find_mentor(app: Container, user: Optional[User] = None) -> None:
    ui.subheader("Find a mentor")
    talent = ui.ask("Talent path (Enter for all)", required=False)
    location = ui.ask("Location (Enter for anywhere)", required=False)
    mentors = app.mentorship.find_mentors(talent, location)
    if not mentors:
        ui.info("No mentors match that search yet.")
        return
    show_mentors(mentors)
    if user and ui.confirm("\nSend a mentorship request?"):
        mentor_id = ui.ask_int("Mentor ID")
        message = ui.ask("Short message to the mentor")
        req = app.mentorship.request(user, mentor_id, message)
        ui.success(f"Request sent to {req.mentor_name}. You'll see their reply under "
                   "'My mentorship requests'.")
