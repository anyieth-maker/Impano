"""Automated tests. Run with:  python -m unittest discover tests -v

Each test uses a fresh in-memory SQLite database, so the real impano.db is
never touched.
"""

import unittest
from datetime import date, timedelta

from impano.container import Container
from impano.services.errors import (AuthenticationError, NotFoundError,
                                    PermissionDeniedError, ValidationError)

FUTURE = (date.today() + timedelta(days=10)).isoformat()


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = Container(":memory:")
        self.admin = self.app.auth.login("admin", "admin123")
        self.mentor = self.app.auth.login("amani", "mentor123")
        self.member = self.app.auth.login("keza", "member123")
        self.music = self.app.admin.talent_paths.get_by_name("Music")

    def tearDown(self):
        self.app.close()


class TestAuth(BaseTest):
    def test_register_and_login(self):
        user = self.app.auth.register("Test User", "tester", "secret1", "+250788999000", "Kigali")
        self.assertEqual(user.role, "member")
        self.assertEqual(self.app.auth.login("tester", "secret1").id, user.id)

    def test_password_is_not_stored_in_plain_text(self):
        row = self.app.db.fetch_one("SELECT password_hash FROM users WHERE username='admin'")
        self.assertNotEqual(row["password_hash"], "admin123")

    def test_wrong_password(self):
        with self.assertRaises(AuthenticationError):
            self.app.auth.login("admin", "wrong")

    def test_duplicate_username(self):
        with self.assertRaises(ValidationError):
            self.app.auth.register("X", "keza", "secret1", "+250788999000", "Kigali")

    def test_invalid_phone(self):
        with self.assertRaises(ValidationError):
            self.app.auth.register("X", "newguy", "secret1", "abc", "Kigali")

    def test_update_profile(self):
        updated = self.app.auth.update_profile(self.member, "Keza U.", "+250785550000",
                                               "Huye", self.music.id, "Singer")
        self.assertEqual(updated.location, "Huye")


class TestPrograms(BaseTest):
    def test_search_by_talent_path(self):
        results = self.app.programs.search("carpentry")
        self.assertTrue(results)
        self.assertTrue(all(p.talent_path == "Carpentry" for p in results))

    def test_search_by_location(self):
        results = self.app.programs.search("Music", "Juba")
        self.assertEqual([p.location for p in results], ["Juba"])

    def test_search_by_category(self):
        self.assertTrue(all(p.category == "Sports" for p in self.app.programs.search("Sports")))

    def test_empty_search_rejected(self):
        with self.assertRaises(ValidationError):
            self.app.programs.search("   ")

    def test_admin_crud(self):
        p = self.app.programs.create(self.admin, "Drumming", "", self.music.id,
                                     "Hub", "Kigali", "+250788000000")
        p = self.app.programs.update(self.admin, p.id, "Drumming 2", "", self.music.id,
                                     "Hub", "Musanze", "+250788000000")
        self.assertEqual(p.location, "Musanze")
        self.app.programs.delete(self.admin, p.id)
        with self.assertRaises(NotFoundError):
            self.app.programs.get(p.id)

    def test_member_cannot_create_program(self):
        with self.assertRaises(PermissionDeniedError):
            self.app.programs.create(self.member, "X", "", self.music.id, "H", "K", "C")

    def test_favorites(self):
        program = self.app.programs.search("Music")[0]
        self.app.programs.save_favorite(self.member, program.id)
        self.app.programs.save_favorite(self.member, program.id)  # no duplicate
        self.assertEqual(len(self.app.programs.favorites(self.member)), 1)
        self.app.programs.remove_favorite(self.member, program.id)
        self.assertEqual(self.app.programs.favorites(self.member), [])


class TestWorkshops(BaseTest):
    def test_register_reduces_seats(self):
        w = self.app.workshops.upcoming()[0]
        updated = self.app.workshops.register(self.member, w.id, "Keza", "+250785551234")
        self.assertEqual(updated.seats_left, w.seats_left - 1)
        self.assertEqual(len(self.app.workshops.my_registrations(self.member)), 1)

    def test_cannot_register_twice(self):
        w = self.app.workshops.upcoming()[0]
        self.app.workshops.register(self.member, w.id, "Keza", "+250785551234")
        with self.assertRaises(ValidationError):
            self.app.workshops.register(self.member, w.id, "Keza", "+250785551234")

    def test_full_workshop(self):
        w = self.app.workshops.create(self.mentor, "Tiny", "", None, "Kigali", FUTURE, 1)
        self.app.workshops.register(self.member, w.id, "Keza", "+250785551234")
        with self.assertRaises(ValidationError):
            self.app.workshops.register(self.admin, w.id, "Admin", "+250700000000")

    def test_unknown_workshop(self):
        with self.assertRaises(NotFoundError):
            self.app.workshops.register(self.member, 999, "Keza", "+250785551234")

    def test_past_date_rejected(self):
        with self.assertRaises(ValidationError):
            self.app.workshops.create(self.mentor, "Old", "", None, "Kigali", "2000-01-01", 5)

    def test_mentor_cannot_edit_others_workshop(self):
        admin_ws = self.app.workshops.create(self.admin, "Admin WS", "", None, "Kigali", FUTURE, 5)
        with self.assertRaises(PermissionDeniedError):
            self.app.workshops.delete(self.mentor, admin_ws.id)

    def test_cancel_registration(self):
        w = self.app.workshops.upcoming()[0]
        self.app.workshops.register(self.member, w.id, "Keza", "+250785551234")
        self.app.workshops.cancel(self.member, w.id)
        self.assertEqual(self.app.workshops.my_registrations(self.member), [])

    def test_attendees_visible_to_host(self):
        w = self.app.workshops.create(self.mentor, "Mine", "", None, "Kigali", FUTURE, 5)
        self.app.workshops.register(self.member, w.id, "Keza", "+250785551234")
        self.assertEqual(len(self.app.workshops.attendees(self.mentor, w.id)), 1)


class TestJobs(BaseTest):
    def test_discover_by_category(self):
        jobs = self.app.jobs.discover("arts")
        self.assertTrue(jobs)
        self.assertTrue(all(j.category == "Arts" for j in jobs))

    def test_invalid_category(self):
        with self.assertRaises(ValidationError):
            self.app.jobs.discover("Cooking")

    def test_closed_jobs_hidden(self):
        job = self.app.jobs.create(self.mentor, "Gig", "", self.music.id, "Kigali", "c", "call")
        self.app.jobs.update(self.mentor, job.id, job.title, "", self.music.id,
                             "Kigali", "c", "call", is_open=False)
        self.assertNotIn(job.id, [j.id for j in self.app.jobs.discover("Arts")])

    def test_member_cannot_post(self):
        with self.assertRaises(PermissionDeniedError):
            self.app.jobs.create(self.member, "X", "", self.music.id, "K", "c", "h")


class TestMentorship(BaseTest):
    def test_request_and_accept(self):
        req = self.app.mentorship.request(self.member, self.mentor.id, "Please teach me")
        self.assertEqual(req.status, "pending")
        with self.assertRaises(ValidationError):
            self.app.mentorship.request(self.member, self.mentor.id, "Again")
        accepted = self.app.mentorship.respond(self.mentor, req.id, accept=True)
        self.assertEqual(accepted.status, "accepted")
        with self.assertRaises(ValidationError):
            self.app.mentorship.respond(self.mentor, req.id, accept=False)

    def test_cannot_request_non_mentor(self):
        with self.assertRaises(NotFoundError):
            self.app.mentorship.request(self.mentor, self.member.id, "hi")

    def test_find_mentors_by_talent(self):
        names = [m.username for m in self.app.mentorship.find_mentors("Carpentry")]
        self.assertEqual(names, ["amani"])


class TestAdmin(BaseTest):
    def test_change_role(self):
        self.assertEqual(self.app.admin.change_role(self.admin, self.member.id, "mentor").role, "mentor")

    def test_cannot_change_own_role(self):
        with self.assertRaises(ValidationError):
            self.app.admin.change_role(self.admin, self.admin.id, "member")

    def test_member_cannot_list_users(self):
        with self.assertRaises(PermissionDeniedError):
            self.app.admin.list_users(self.member)

    def test_delete_user_cascades(self):
        w = self.app.workshops.upcoming()[0]
        self.app.workshops.register(self.member, w.id, "Keza", "+250785551234")
        self.app.admin.delete_user(self.admin, self.member.id)
        self.assertEqual(self.app.db.scalar("SELECT COUNT(*) FROM workshop_registrations"), 0)

    def test_talent_path_crud(self):
        p = self.app.admin.create_talent_path(self.admin, "pottery", "arts")
        self.assertEqual((p.name, p.category), ("Pottery", "Arts"))
        with self.assertRaises(ValidationError):
            self.app.admin.create_talent_path(self.admin, "Pottery", "Arts")
        self.app.admin.update_talent_path(self.admin, p.id, "Ceramics", "Trades")
        self.app.admin.delete_talent_path(self.admin, p.id)
        with self.assertRaises(NotFoundError):
            self.app.admin.get_talent_path(p.id)

    def test_statistics(self):
        stats = self.app.admin.statistics(self.admin)
        self.assertEqual(stats["Admins"], 1)
        self.assertGreater(stats["Training programs"], 0)


if __name__ == "__main__":
    unittest.main()
