"""Menu for administrators: full CRUD over every table + statistics."""

from __future__ import annotations

from impano.container import Container
from impano.models import ROLES, User
from impano.services.validators import validate_date
from . import shared, ui
from .mentor_menu import manage_jobs, manage_workshops


class AdminMenu:
    def __init__(self, app: Container, user: User) -> None:
        self.app = app
        self.user = user

    def run(self) -> None:
        ui.run_menu(
            f"ADMIN MENU - {self.user.full_name}",
            {
                "1": ("Manage training programs", self.programs_menu),
                "2": ("Manage talent paths", self.talent_paths_menu),
                "3": ("Create a workshop", self.create_workshop),
                "4": ("Manage workshops & attendees", lambda: manage_workshops(self.app, self.user)),
                "5": ("Manage job postings", lambda: manage_jobs(self.app, self.user)),
                "6": ("Manage users & roles", self.users_menu),
                "7": ("Platform statistics", self.stats),
            },
            exit_label="Log out",
        )

    # ---------------------------------------------------- training programs
    def programs_menu(self):
        ui.run_menu("TRAINING PROGRAMS", {
            "1": ("List all programs", self.list_programs),
            "2": ("Add a program", self.add_program),
            "3": ("Edit a program", self.edit_program),
            "4": ("Delete a program", self.delete_program),
        })
        return False

    def list_programs(self):
        programs = self.app.programs.list_all()
        ui.table(["ID", "Program", "Talent path", "Center", "Location"],
                 [(p.id, p.name, p.talent_path, p.center_name, p.location) for p in programs],
                 empty="No programs yet.")

    def add_program(self):
        ui.subheader("Add training program")
        name = ui.ask("Program name")
        description = ui.ask("Description", required=False)
        path_id = shared.pick_talent_path(self.app)
        center = ui.ask("Center name")
        location = ui.ask("Location")
        contact = ui.ask("Contact")
        p = self.app.programs.create(self.user, name, description, path_id, center, location, contact)
        ui.success(f"Program '{p.name}' added with ID {p.id}.")

    def edit_program(self):
        self.list_programs()
        p = self.app.programs.get(ui.ask_int("\nProgram ID to edit"))
        ui.info("Press Enter to keep the current value.")
        name = ui.ask("Program name", default=p.name)
        description = ui.ask("Description", required=False, default=p.description)
        path_id = shared.pick_talent_path(self.app, current=p.talent_path_id)
        center = ui.ask("Center name", default=p.center_name)
        location = ui.ask("Location", default=p.location)
        contact = ui.ask("Contact", default=p.contact)
        self.app.programs.update(self.user, p.id, name, description, path_id,
                                 center, location, contact)
        ui.success("Program updated.")

    def delete_program(self):
        self.list_programs()
        program_id = ui.ask_int("\nProgram ID to delete")
        p = self.app.programs.get(program_id)
        if ui.confirm(f"Delete '{p.name}'?"):
            self.app.programs.delete(self.user, program_id)
            ui.success("Program deleted.")

    # --------------------------------------------------------- talent paths
    def talent_paths_menu(self):
        ui.run_menu("TALENT PATHS", {
            "1": ("List talent paths", self.list_paths),
            "2": ("Add a talent path", self.add_path),
            "3": ("Edit a talent path", self.edit_path),
            "4": ("Delete a talent path", self.delete_path),
        })
        return False

    def list_paths(self):
        paths = self.app.admin.list_talent_paths()
        ui.table(["ID", "Talent path", "Category"], [(p.id, p.name, p.category) for p in paths])

    def add_path(self):
        name = ui.ask("Talent path name")
        category = shared.pick_category()
        p = self.app.admin.create_talent_path(self.user, name, category)
        ui.success(f"Talent path '{p.name}' ({p.category}) added.")

    def edit_path(self):
        self.list_paths()
        p = self.app.admin.get_talent_path(ui.ask_int("\nTalent path ID to edit"))
        name = ui.ask("New name", default=p.name)
        print(f"Current category: {p.category}")
        category = shared.pick_category()
        self.app.admin.update_talent_path(self.user, p.id, name, category)
        ui.success("Talent path updated.")

    def delete_path(self):
        self.list_paths()
        p = self.app.admin.get_talent_path(ui.ask_int("\nTalent path ID to delete"))
        ui.info("Warning: programs and jobs in this path will also be deleted.")
        if ui.confirm(f"Delete '{p.name}'?"):
            self.app.admin.delete_talent_path(self.user, p.id)
            ui.success("Talent path deleted.")

    # ------------------------------------------------------------ workshops
    def create_workshop(self):
        ui.subheader("Create workshop")
        title = ui.ask("Title")
        description = ui.ask("Description", required=False)
        path_id = shared.pick_talent_path(self.app, required=False)
        location = ui.ask("Location / venue")
        event_date = ui.ask_valid("Date (YYYY-MM-DD)", validate_date)
        capacity = ui.ask_int("Capacity")
        w = self.app.workshops.create(self.user, title, description, path_id,
                                      location, event_date, capacity)
        ui.success(f"Workshop '{w.title}' created with ID {w.id}.")

    # ---------------------------------------------------------------- users
    def users_menu(self):
        ui.run_menu("USERS & ROLES", {
            "1": ("List all users", self.list_users),
            "2": ("Change a user's role", self.change_role),
            "3": ("Delete a user", self.delete_user),
        })
        return False

    def list_users(self):
        users = self.app.admin.list_users(self.user)
        ui.table(["ID", "Name", "Username", "Role", "Location", "Talent path"],
                 [(u.id, u.full_name, u.username, u.role, u.location, u.talent_path or "-")
                  for u in users])

    def change_role(self):
        self.list_users()
        user_id = ui.ask_int("\nUser ID")
        role = ui.ask(f"New role ({' / '.join(ROLES)})")
        u = self.app.admin.change_role(self.user, user_id, role)
        ui.success(f"{u.full_name} is now a {u.role}.")

    def delete_user(self):
        self.list_users()
        user_id = ui.ask_int("\nUser ID to delete")
        if ui.confirm("This also deletes their registrations and requests. Continue?"):
            self.app.admin.delete_user(self.user, user_id)
            ui.success("User deleted.")

    # ---------------------------------------------------------------- stats
    def stats(self):
        ui.subheader("Platform statistics")
        for label, value in self.app.admin.statistics(self.user).items():
            print(f"  {label:<24}{value:>6}")
