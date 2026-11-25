"""Sample data so the app is useful (and demo-ready) on first launch.

Runs only when the talent_paths table is empty, so it never overwrites real data.
Demo accounts (username / password):
    admin   / admin123   -> admin
    amani   / mentor123  -> mentor (Carpentry, Kigali)
    grace   / mentor123  -> mentor (Music, Juba)
    keza    / member123  -> member (Music, Kigali)
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from impano.container import Container

TALENT_PATHS = [
    ("Carpentry", "Trades"), ("Tailoring", "Trades"), ("Welding", "Trades"),
    ("Hairdressing", "Trades"), ("Music", "Arts"), ("Painting", "Arts"),
    ("Dance", "Arts"), ("Photography", "Arts"), ("Football", "Sports"),
    ("Basketball", "Sports"), ("Athletics", "Sports"),
]

PROGRAMS = [
    ("Furniture Making Basics", "6-week hands-on furniture course", "Carpentry",
     "Kigali Vocational Hub", "Kigali", "+250788000111"),
    ("Advanced Joinery", "Cabinets, doors and roofing frames", "Carpentry",
     "Juba Technical Centre", "Juba", "+211912000222"),
    ("Fashion & Tailoring Lab", "Pattern cutting and machine sewing", "Tailoring",
     "Nyamirambo Women's Centre", "Kigali", "+250788000333"),
    ("Metal Works Starter", "Safety, arc welding and fabrication", "Welding",
     "Bujumbura Skills Institute", "Bujumbura", "+25779000444"),
    ("Music Production Bootcamp", "Recording, mixing and beat making", "Music",
     "Kigali Music Academy", "Kigali", "+250788000555"),
    ("Live Band & Vocals", "Instruments, vocals and stage performance", "Music",
     "Juba Arts Collective", "Juba", "+211912000666"),
    ("Street Art & Murals", "Painting large public works", "Painting",
     "Inema Arts Centre", "Kigali", "+250788000777"),
    ("Youth Football Academy", "Coaching for 15-25 year olds", "Football",
     "Amahoro Sports Grounds", "Kigali", "+250788000888"),
    ("Basketball Skills Camp", "Fundamentals and team play", "Basketball",
     "Juba Youth Sports Club", "Juba", "+211912000999"),
    ("Portrait Photography 101", "Lighting, editing and client work", "Photography",
     "Nairobi Creative Space", "Nairobi", "+254700000123"),
]


def _future(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def seed_if_empty(c: "Container") -> None:
    if c.db.scalar("SELECT COUNT(*) FROM talent_paths"):
        return

    # Talent paths
    path_ids = {}
    for name, category in TALENT_PATHS:
        path_ids[name] = c.db.insert(
            "INSERT INTO talent_paths (name, category) VALUES (?, ?)", (name, category)
        )

    # Users (created through the service so passwords are hashed properly)
    admin = c.auth.register("Impano Admin", "admin", "admin123", "+250700000000",
                            "Kigali", role="admin")
    amani = c.auth.register("Amani Habimana", "amani", "mentor123", "+250781234567",
                            "Kigali", path_ids["Carpentry"], role="mentor",
                            bio="Master carpenter with 12 years of experience.")
    grace = c.auth.register("Grace Ladu", "grace", "mentor123", "+211921234567",
                            "Juba", path_ids["Music"], role="mentor",
                            bio="Producer and vocal coach. Runs a community studio.")
    c.auth.register("Brian Mugisha", "brian", "mentor123", "+250789876543",
                    "Kigali", path_ids["Football"], role="mentor",
                    bio="Former national league player, now youth coach.")
    c.auth.register("Keza Uwase", "keza", "member123", "+250785551234",
                    "Kigali", path_ids["Music"], role="member")

    # Training programs
    for name, desc, path, center, location, contact in PROGRAMS:
        c.db.insert(
            """INSERT INTO training_programs
                   (name, description, talent_path_id, center_name, location, contact)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, desc, path_ids[path], center, location, contact),
        )

    # Workshops (dates are always in the future, relative to today)
    workshops = [
        ("Skills Are Education Too", "Awareness talk for parents and youth on the value of trades",
         None, "Kigali Public Library", _future(5), 40, admin.id),
        ("Intro to Woodwork", "Build a stool in one afternoon", path_ids["Carpentry"],
         "Kigali Vocational Hub", _future(9), 12, amani.id),
        ("Songwriting Circle", "Write and perform an original song", path_ids["Music"],
         "Juba Arts Collective", _future(12), 2, grace.id),
        ("Pricing Your Craft", "How artisans set fair prices and find clients", None,
         "Online (Zoom)", _future(16), 100, admin.id),
    ]
    for w in workshops:
        c.db.insert(
            """INSERT INTO workshops
                   (title, description, talent_path_id, location, event_date, capacity, host_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""", w,
        )

    # Job and business opportunities
    jobs = [
        ("Apprentice Carpenter", "Paid apprenticeship, tools provided", "Carpentry", "Kigali",
         "+250781234567", "Call Amani or visit Kigali Vocational Hub on weekdays", amani.id),
        ("Wedding Band Vocalist", "Weekend gigs, pay per event", "Music", "Juba",
         "+211921234567", "Send a 1-minute voice note to the contact number", grace.id),
        ("Mural Painter for Hotel", "3-week contract, materials supplied", "Painting", "Kigali",
         "murals@kigalihotel.rw", "Email 3 photos of previous work", admin.id),
        ("Junior Football Coach", "Part-time, Saturdays", "Football", "Kigali",
         "+250789876543", "Apply in person at Amahoro Sports Grounds", admin.id),
        ("Tailor for School Uniforms", "Seasonal contract, Dec-Jan", "Tailoring", "Bujumbura",
         "+25779000444", "Visit with a sample garment", admin.id),
    ]
    for title, desc, path, location, contact, how, poster in jobs:
        c.db.insert(
            """INSERT INTO job_postings
                   (title, description, talent_path_id, location, contact, how_to_apply, posted_by)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, desc, path_ids[path], location, contact, how, poster),
        )
