"""Terminal input/output helpers shared by every menu.

All keyboard input goes through these functions, so invalid input (letters
instead of numbers, empty answers) is handled in one place and never crashes
the program.
"""

from __future__ import annotations

import getpass
import sys
import textwrap
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from impano.services.errors import ImpanoError

WIDTH = 64

# ANSI colours (disabled automatically when output is not a terminal)
_USE_COLOR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def header(title: str) -> None:
    print("\n" + "=" * WIDTH)
    print(_c("1;36", title.center(WIDTH)))
    print("=" * WIDTH)


def subheader(title: str) -> None:
    print("\n" + _c("1", f"--- {title} ---"))


def success(msg: str) -> None:
    print(_c("32", f"[OK] {msg}"))


def error(msg: str) -> None:
    print(_c("31", f"[!] {msg}"))


def info(msg: str) -> None:
    print(_c("33", msg))


def wrap(text: str, indent: str = "    ") -> str:
    return textwrap.fill(text, WIDTH, initial_indent=indent, subsequent_indent=indent)


# ------------------------------------------------------------------ input
def ask(prompt: str, required: bool = True, default: Optional[str] = None) -> str:
    """Ask for text. Pressing Enter keeps ``default`` when one is given."""
    suffix = f" [{default}]" if default not in (None, "") else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if not value and default is not None:
            return default
        if value or not required:
            return value
        error("This field is required.")


def ask_valid(prompt: str, validator: Callable[[str], str],
              default: Optional[str] = None) -> str:
    """Ask until ``validator`` accepts the value (used for dates and phone numbers)."""
    while True:
        try:
            return validator(ask(prompt, default=default))
        except ImpanoError as exc:
            error(str(exc))


def ask_int(prompt: str, required: bool = True, default: Optional[int] = None) -> Optional[int]:
    """Ask for a whole number; re-asks on letters instead of crashing."""
    while True:
        raw = ask(prompt, required=required and default is None,
                  default=str(default) if default is not None else None)
        if raw == "" and not required:
            return None
        try:
            return int(raw)
        except ValueError:
            error("Please type a number.")


def ask_password(prompt: str = "Password") -> str:
    if sys.stdin.isatty():
        return getpass.getpass(f"{prompt}: ")
    return input(f"{prompt}: ")  # piped input (tests / scripted demo)


def confirm(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        error("Please type y or n.")


def pause() -> None:
    input("\nPress Enter to continue...")


# ------------------------------------------------------------------ output
def table(headers: Sequence[str], rows: List[Sequence], empty: str = "Nothing to show.") -> None:
    if not rows:
        info(empty)
        return
    data = [[str(x) for x in r] for r in rows]
    widths = [min(max(len(h), *(len(r[i]) for r in data)), 28) for i, h in enumerate(headers)]

    def fmt(cells):
        return " | ".join(c[:w].ljust(w) for c, w in zip(cells, widths))

    print(fmt(headers))
    print("-+-".join("-" * w for w in widths))
    for r in data:
        print(fmt(r))


# ------------------------------------------------------------------ menus
MenuOptions = Dict[str, Tuple[str, Callable[[], Optional[bool]]]]


def run_menu(title: str, options: MenuOptions, exit_label: str = "Back",
             intro: Optional[Callable[[], None]] = None) -> None:
    """Show a numbered menu until the user picks 0.

    A handler may return True to leave the menu, or False to skip the
    "Press Enter" pause (used when it ran its own sub-menu).
    Expected errors from the services are shown nicely and the loop continues.
    """
    while True:
        header(title)
        if intro:
            intro()
        for key, (label, _) in options.items():
            print(f"  {key}. {label}")
        print(f"  0. {exit_label}")
        choice = input(f"\nType a number (0-{len(options)}) and press Enter: ").strip()
        if choice == "0":
            return
        if choice not in options:
            error("Invalid choice, please pick one of the numbers shown.")
            continue
        try:
            result = options[choice][1]()
            if result is True:      # e.g. log out
                return
            if result is False:     # handler opened its own sub-menu; no pause needed
                continue
        except ImpanoError as exc:
            error(str(exc))
        pause()
