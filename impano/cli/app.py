"""Entry screens: welcome menu, log in, sign up, guest mode, role routing."""

from __future__ import annotations

from impano import APP_NAME
from impano.container import Container
from impano.models import User
from impano.services.validators import validate_phone
from . import shared, ui
from .admin_menu import AdminMenu
from .member_menu import MemberMenu
from .mentor_menu import MentorMenu

ROLE_MENUS = {"member": MemberMenu, "mentor": MentorMenu, "admin": AdminMenu}


class ImpanoCLI:
    def __init__(self, app: Container) -> None:
        self.app = app

    def run(self) -> None:
        ui.run_menu(
            f"WELCOME TO {APP_NAME} APP",
            {
                "1": ("Log in", self.login),
                "2": ("Create an account", self.sign_up),
                "3": ("Browse as guest (programs, jobs, mentors)", self.guest),
            },
            exit_label="Exit program",
            intro=lambda: print("Your talent is your education.\n"
                                "Find training, workshops, mentors and jobs.\n"),
        )
        print("\nThank you for using Impano. Goodbye!\n")

    # ---------------------------------------------------------------- auth
    def login(self):
        ui.subheader("Log in")
        username = ui.ask("Username")
        password = ui.ask_password()
        user = self.app.auth.login(username, password)
        ui.success(f"Welcome back, {user.full_name}! (role: {user.role})")
        self.open_role_menu(user)
        return False

    def sign_up(self):
        ui.subheader("Create an account")
        print("  1. Member - I want to grow my talent")
        print("  2. Mentor - I want to guide others")
        role = "mentor" if ui.ask("Account type", default="1") == "2" else "member"
        full_name = ui.ask("Full name")
        username = ui.ask("Username (3-20 letters/numbers)")
        password = ui.ask_password("Password (min 6 characters)")
        phone = ui.ask_valid("Phone number (e.g. +250788123456)", validate_phone)
        location = ui.ask("Location (city / district)")
        print("\nChoose your talent path:")
        path_id = shared.pick_talent_path(self.app, required=False)
        bio = ui.ask("Short bio (experience, what you offer)", required=False) if role == "mentor" else ""
        user = self.app.auth.register(full_name, username, password, phone, location,
                                      path_id, role=role, bio=bio)
        ui.success(f"Account created! Welcome to Impano, {user.full_name}.")
        self.open_role_menu(user)
        return False

    def open_role_menu(self, user: User) -> None:
        ROLE_MENUS[user.role](self.app, user).run()
        ui.info("You have been logged out.")

    # --------------------------------------------------------------- guest
    def guest(self):
        ui.run_menu(
            "GUEST MODE",
            {
                "1": ("Search talent paths & training centers", lambda: shared.search_programs(self.app)),
                "2": ("Discover job and business opportunities", lambda: shared.discover_jobs(self.app)),
                "3": ("Browse mentors", lambda: shared.find_mentor(self.app)),
                "4": ("See upcoming workshops", lambda: shared.show_workshops(self.app.workshops.upcoming())),
            },
            intro=lambda: ui.info("Create an account to register for workshops and contact mentors.\n"),
        )
        return False
