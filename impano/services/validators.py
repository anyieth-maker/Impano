"""Reusable input checks. Each raises ValidationError when the value is bad."""

from __future__ import annotations

import re
from datetime import date, datetime

from impano.models import CATEGORIES, ROLES
from .errors import ValidationError

PHONE_RE = re.compile(r"^\+?\d{9,15}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")


def require_text(value: str, field: str, max_len: int = 200) -> str:
    value = (value or "").strip()
    if not value:
        raise ValidationError(f"{field} cannot be empty.")
    if len(value) > max_len:
        raise ValidationError(f"{field} must be at most {max_len} characters.")
    return value


def validate_phone(phone: str) -> str:
    cleaned = re.sub(r"[\s-]", "", phone or "")
    if not PHONE_RE.match(cleaned):
        raise ValidationError("Phone number must be 9-15 digits (an optional leading + is allowed).")
    return cleaned


def validate_username(username: str) -> str:
    username = (username or "").strip()
    if not USERNAME_RE.match(username):
        raise ValidationError("Username must be 3-20 letters, numbers or underscores.")
    return username


def validate_password(password: str) -> str:
    if len(password or "") < 6:
        raise ValidationError("Password must be at least 6 characters.")
    return password


def validate_date(value: str, allow_past: bool = False) -> str:
    try:
        parsed = datetime.strptime((value or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Date must be in the format YYYY-MM-DD (e.g. 2026-12-05).") from None
    if not allow_past and parsed < date.today():
        raise ValidationError("Date cannot be in the past.")
    return parsed.isoformat()


def validate_positive_int(value, field: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a whole number.") from None
    if number <= 0:
        raise ValidationError(f"{field} must be greater than zero.")
    return number


def validate_category(category: str) -> str:
    for valid in CATEGORIES:
        if (category or "").strip().lower() == valid.lower():
            return valid
    raise ValidationError(f"Category must be one of: {', '.join(CATEGORIES)}.")


def validate_role(role: str) -> str:
    role = (role or "").strip().lower()
    if role not in ROLES:
        raise ValidationError(f"Role must be one of: {', '.join(ROLES)}.")
    return role
