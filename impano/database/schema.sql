-- ============================================================
-- IMPANO database schema (SQLite)
-- All application data lives here. No CSV / JSON storage.
-- ============================================================

-- Talent paths group skills into the three categories from our proposal.
CREATE TABLE IF NOT EXISTS talent_paths (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    category    TEXT    NOT NULL CHECK (category IN ('Arts', 'Trades', 'Sports'))
);

-- Every person using the app. The role column drives which menu they see.
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT    NOT NULL,
    username        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    password_hash   TEXT    NOT NULL,
    salt            TEXT    NOT NULL,
    phone           TEXT    NOT NULL,
    location        TEXT    NOT NULL,
    talent_path_id  INTEGER REFERENCES talent_paths(id) ON DELETE SET NULL,
    role            TEXT    NOT NULL DEFAULT 'member'
                            CHECK (role IN ('member', 'mentor', 'admin')),
    bio             TEXT    NOT NULL DEFAULT '',
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Thing 1 from the proposal: Training Program.
CREATE TABLE IF NOT EXISTS training_programs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    description     TEXT    NOT NULL DEFAULT '',
    talent_path_id  INTEGER NOT NULL REFERENCES talent_paths(id) ON DELETE CASCADE,
    center_name     TEXT    NOT NULL,
    location        TEXT    NOT NULL,
    contact         TEXT    NOT NULL
);

-- Awareness / skills workshops that people can register for.
CREATE TABLE IF NOT EXISTS workshops (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT    NOT NULL,
    description     TEXT    NOT NULL DEFAULT '',
    talent_path_id  INTEGER REFERENCES talent_paths(id) ON DELETE SET NULL,
    location        TEXT    NOT NULL,
    event_date      TEXT    NOT NULL,              -- YYYY-MM-DD
    capacity        INTEGER NOT NULL CHECK (capacity > 0),
    host_id         INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Thing 2 from the proposal: Workshop Registration.
CREATE TABLE IF NOT EXISTS workshop_registrations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    workshop_id     INTEGER NOT NULL REFERENCES workshops(id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    attendee_name   TEXT    NOT NULL,
    phone           TEXT    NOT NULL,
    registered_at   TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (workshop_id, user_id)
);

-- Job and business opportunities, posted by mentors or admins.
CREATE TABLE IF NOT EXISTS job_postings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT    NOT NULL,
    description     TEXT    NOT NULL DEFAULT '',
    talent_path_id  INTEGER NOT NULL REFERENCES talent_paths(id) ON DELETE CASCADE,
    location        TEXT    NOT NULL,
    contact         TEXT    NOT NULL,
    how_to_apply    TEXT    NOT NULL,
    posted_by       INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_open         INTEGER NOT NULL DEFAULT 1 CHECK (is_open IN (0, 1)),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Members asking mentors for guidance.
CREATE TABLE IF NOT EXISTS mentorship_requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mentor_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message         TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'accepted', 'declined')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Bonus feature: bookmarked training programs.
CREATE TABLE IF NOT EXISTS favorites (
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    program_id      INTEGER NOT NULL REFERENCES training_programs(id) ON DELETE CASCADE,
    saved_at        TEXT    NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, program_id)
);
