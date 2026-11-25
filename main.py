"""Run the Impano app:  python main.py

Optional:  python main.py --reset   (delete the database and start with fresh sample data)
"""

import sys

from impano.cli.app import ImpanoCLI
from impano.container import Container
from impano.database.connection import DEFAULT_DB_PATH


def main() -> None:
    if "--reset" in sys.argv and DEFAULT_DB_PATH.exists():
        DEFAULT_DB_PATH.unlink()
        print("Database reset. Fresh sample data will be loaded.")

    app = Container()
    try:
        ImpanoCLI(app).run()
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting Impano. Goodbye!")
    finally:
        app.close()


if __name__ == "__main__":
    main()
