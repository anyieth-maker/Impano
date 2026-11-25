# Presentation Guide: Impano

Run `python main.py --reset` right before you present so the sample data is clean.

## Part 1: Prototype & app journey (15 minutes)

| Time | Who presents | What to show | Keys to type |
|---|---|---|---|
| 0:00–1:30 | Member A | **The problem and GCGOs.** Youth who leave school for trades, arts and sports face stigma and have no network. Impano covers Education, Job Creation, and Arts, Design & Culture. | – |
| 1:30–3:00 | Member A | **Guest journey.** Welcome screen → 3 Browse as guest → 1 search `Music` → 2 jobs → Trades. | `3`, `1`, `Music`, Enter … |
| 3:00–4:30 | Member B | **Sign up as a new member.** Type a bad phone (`12ab`) first to show validation, then a valid one. | `2`, `1`, … |
| 4:30–8:00 | Member B | **Member journey: the 3 core features.** 1 search `carpentry` + `Kigali` → save to favorites. 2 register for workshop 3 (*Songwriting Circle*, 2 seats). Try registering again to show the duplicate check. 3 jobs → Arts. 4 find mentor `Carpentry` → send a request to Amani. 5 favorites. | |
| 8:00–9:00 | Member B | **Crash-proofing.** Type `abc` at a menu, letters at "Workshop ID", and a menu number that doesn't exist. | |
| 9:00–11:30 | Member C | **Mentor journey.** Log out → log in as `amani` / `mentor123`. 1 inbox → accept the request. 2 host a workshop (type a past date first to show validation). 3 view attendees. 4 post a job. | |
| 11:30–12:00 | Member C | Log back in as the member → 7 My mentorship requests now shows **ACCEPTED** and the mentor's phone. This shows the roles interacting through the shared database. | |
| 12:00–14:30 | Member D | **Admin journey.** `admin` / `admin123`. 7 statistics. 1 programs → add, edit, delete. 2 talent paths → add `Pottery`. 6 users → change a role. | |
| 14:30–15:00 | Member D | Close the app and run it again to show the data is still there, because it lives in SQLite. | `0`, `python main.py` |

> Tip: split the presenting between everyone. The rubric grades the group, but the QA questions go to individuals.

## Part 2: QA, where to find each piece of code (5 minutes)

Every member should be able to open these quickly:

| If asked… | Open this file | Look at |
|---|---|---|
| "Where is the main menu loop?" | `impano/cli/ui.py` | `run_menu()` |
| "Where do you stop crashes from bad input?" | `impano/cli/ui.py` | `ask_int()` (`try/except ValueError`), `ask_valid()` |
| "Where does the app connect to the database?" | `impano/database/connection.py` | `Database.__init__()` |
| "Show me your tables" | `impano/database/schema.sql` | – |
| "Where is Feature 1 (search)?" | `cli/shared.py → search_programs()` → `services/program_service.py → search()` → `repositories/program_repository.py → search()` | the `LIKE` query |
| "Where is Feature 2 (workshop registration)?" | `services/workshop_service.py → register()` | capacity / duplicate checks |
| "Where is Feature 3 (jobs)?" | `repositories/job_repository.py → search_by_category()` | `WHERE tp.category = ?` |
| "How do roles work?" | `cli/app.py → ROLE_MENUS`, plus the `_check_admin` / `_check_can_manage` methods in each service | `role` column in `users` |
| "How are passwords stored?" | `services/auth_service.py → hash_password()` | PBKDF2 + salt |
| "Where is your sample data?" | `impano/database/seed.py` | – |
| "How do the layers connect?" | `impano/container.py` | – |
| "Where are your custom exceptions?" | `impano/services/errors.py` | – |
| "Why use `?` in the SQL?" | any repository | Parameterized queries prevent SQL injection |
| "How do you know it works?" | `tests/test_impano.py` | `python -m unittest discover tests -v` |

### Likely questions and short answers
- **Why SQLite rather than MySQL?** It's built into Python and needs no server. It's still a real SQL database, and the same queries would work on MySQL with very small changes.
- **What happens if a workshop fills up?** `WorkshopService.register()` compares the `registered` count with `capacity` and raises `ValidationError("Sorry, this workshop is full.")`.
- **What happens when you delete a talent path?** `ON DELETE CASCADE` deletes its programs and jobs. Users and workshops in that path have the path set to NULL instead.
- **Why separate services and repositories?** Repositories only know SQL. Services only know the rules. Each piece can be changed or tested on its own.
