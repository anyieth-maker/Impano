"""Menu for the main user: a young person with a trade, art or sport talent."""

from __future__ import annotations

from impano.container import Container
from impano.models import User
from . import shared, ui


class MemberMenu:
    def __init__(self, app: Container, user: User) -> None:
        self.app = app
        self.user = user

    def run(self) -> None:
        ui.run_menu(
            f"MEMBER MENU - {self.user.full_name}",
            {
                "1": ("Search talent paths & training centers", self.search),
                "2": ("Register for awareness workshops", self.register),
                "3": ("Discover job and business opportunities", self.jobs),
                "4": ("Find a mentor", self.mentor),
                "5": ("My favorite programs", self.favorites),
                "6": ("My workshop registrations", self.registrations),
                "7": ("My mentorship requests", self.my_requests),
                "8": ("View / edit my profile", self.profile),
            },
            exit_label="Log out",
            intro=lambda: print("What would you like to do today?\n"),
        )

    # Core features (from the PLP-1 proposal)
    def search(self):
        shared.search_programs(self.app, self.user)

    def register(self):
        shared.register_workshop(self.app, self.user)

    def jobs(self):
        shared.discover_jobs(self.app)

    def mentor(self):
        shared.find_mentor(self.app, self.user)

    # Bonus: favorites
    def favorites(self):
        ui.subheader("My favorite programs")
        favs = self.app.programs.favorites(self.user)
        if not favs:
            ui.info("You have no favorites yet. Save some from 'Search talent paths'.")
            return
        shared.show_programs(favs)
        if ui.confirm("\nRemove a program from favorites?"):
            self.app.programs.remove_favorite(self.user, ui.ask_int("Program ID"))
            ui.success("Removed from favorites.")

    def registrations(self):
        ui.subheader("My workshop registrations")
        regs = self.app.workshops.my_registrations(self.user)
        ui.table(["Workshop ID", "Title", "Date", "Location"],
                 [(r.workshop_id, r.workshop_title, r.event_date, r.location) for r in regs],
                 empty="You have not registered for any workshops yet.")
        if regs and ui.confirm("\nCancel a registration?"):
            self.app.workshops.cancel(self.user, ui.ask_int("Workshop ID"))
            ui.success("Registration cancelled.")

    def my_requests(self):
        ui.subheader("My mentorship requests")
        reqs = self.app.mentorship.sent_by(self.user)
        ui.table(["ID", "Mentor", "Status", "Contact (if accepted)", "Sent"],
                 [(r.id, r.mentor_name, r.status.upper(),
                   r.mentor_phone if r.status == "accepted" else "-",
                   r.created_at[:10]) for r in reqs],
                 empty="You have not sent any mentorship requests yet.")

    def profile(self):
        self.user = shared.edit_profile(self.app, self.user)
