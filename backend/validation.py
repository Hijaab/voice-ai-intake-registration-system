import re
from datetime import date
from typing import Optional


# =========================================================
# NAME VALIDATION
# =========================================================

NAME_PATTERN = re.compile(
    r"^[A-Za-z]+(?:[-'][A-Za-z]+)*$"
)


def validate_name(value: str, field_name: str) -> str:

    value = value.strip()

    if not value:
        raise ValueError(
            f"{field_name} is required."
        )

    if len(value) > 50:
        raise ValueError(
            f"{field_name} must not exceed 50 characters."
        )

    if not NAME_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field_name} may contain only letters, "
            "hyphens, and apostrophes."
        )

    return value


# =========================================================
# PHONE VALIDATION
# =========================================================

def normalize_phone(value: str) -> str:

    digits = re.sub(
        r"\D",
        "",
        value,
    )

    # Handle +1 / 1 prefix
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) != 10:
        raise ValueError(
            "Phone number must be a valid 10-digit U.S. phone number."
        )

    return digits


# =========================================================
# DATE OF BIRTH
# =========================================================

def validate_date_of_birth(value: date) -> date:

    today = date.today()

    if value > today:
        raise ValueError(
            "Date of birth cannot be in the future."
        )

    return value


# =========================================================
# STATE
# =========================================================

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT",
    "DE", "FL", "GA", "HI", "ID", "IL", "IN",
    "IA", "KS", "KY", "LA", "ME", "MD", "MA",
    "MI", "MN", "MS", "MO", "MT", "NE", "NV",
    "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN",
    "TX", "UT", "VT", "VA", "WA", "WV", "WI",
    "WY", "DC",
}


def validate_state(value: str) -> str:

    value = value.strip().upper()

    if value not in US_STATES:
        raise ValueError(
            "State must be a valid two-letter U.S. state abbreviation."
        )

    return value


# =========================================================
# ZIP CODE
# =========================================================

ZIP_PATTERN = re.compile(
    r"^\d{5}(?:-\d{4})?$"
)


def validate_zip(value: str) -> str:

    value = value.strip()

    if not ZIP_PATTERN.fullmatch(value):
        raise ValueError(
            "ZIP code must be 5 digits or ZIP+4 format."
        )

    return value


# =========================================================
# EMERGENCY PHONE
# =========================================================

def validate_optional_phone(
    value: Optional[str],
) -> Optional[str]:

    if value is None:
        return None

    if not value.strip():
        return None

    return normalize_phone(value)