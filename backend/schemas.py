import re
from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


VALID_SEXES = {
    "Male",
    "Female",
    "Other",
    "Decline to Answer",
}


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


NAME_PATTERN = re.compile(
    r"^[A-Za-z]+(?:[A-Za-z'-]*[A-Za-z])?$"
)

ZIP_PATTERN = re.compile(
    r"^\d{5}(?:-\d{4})?$"
)


def validate_name(value: str, field_name: str) -> str:
    value = value.strip()

    if not 1 <= len(value) <= 50:
        raise ValueError(
            f"{field_name} must be between 1 and 50 characters."
        )

    if not NAME_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field_name} may contain only letters, "
            "hyphens, and apostrophes."
        )

    return value


def normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)

    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) != 10:
        raise ValueError(
            "Phone number must be a valid 10-digit US phone number."
        )

    if digits[0] not in "23456789":
        raise ValueError(
            "Phone number must contain a valid US area code."
        )

    return digits


class PatientBase(BaseModel):

    first_name: str = Field(
        min_length=1,
        max_length=50
    )

    last_name: str = Field(
        min_length=1,
        max_length=50
    )

    date_of_birth: date

    sex: str

    phone_number: str

    email: Optional[EmailStr] = None

    address_line_1: str = Field(
        min_length=1,
        max_length=200
    )

    address_line_2: Optional[str] = Field(
        default=None,
        max_length=200
    )

    city: str = Field(
        min_length=1,
        max_length=100
    )

    state: str

    zip_code: str

    insurance_provider: Optional[str] = Field(
        default=None,
        max_length=150
    )

    insurance_member_id: Optional[str] = Field(
        default=None,
        max_length=100
    )

    preferred_language: str = Field(
        default="English",
        max_length=50
    )

    emergency_contact_name: Optional[str] = Field(
        default=None,
        max_length=150
    )

    emergency_contact_phone: Optional[str] = None


    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value):
        return validate_name(value, "First name")


    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value):
        return validate_name(value, "Last name")


    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value):
        if value > date.today():
            raise ValueError(
                "Date of birth cannot be in the future."
            )

        return value


    @field_validator("sex")
    @classmethod
    def validate_sex(cls, value):
        if value not in VALID_SEXES:
            raise ValueError(
                "Sex must be Male, Female, Other, "
                "or Decline to Answer."
            )

        return value


    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value):
        return normalize_phone(value)


    @field_validator("emergency_contact_phone")
    @classmethod
    def validate_emergency_phone(cls, value):
        if value is None:
            return None

        return normalize_phone(value)


    @field_validator("state")
    @classmethod
    def validate_state(cls, value):
        value = value.strip().upper()

        if value not in US_STATES:
            raise ValueError(
                "State must be a valid 2-letter US state abbreviation."
            )

        return value


    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, value):
        value = value.strip()

        if not ZIP_PATTERN.fullmatch(value):
            raise ValueError(
                "ZIP code must be 5 digits or ZIP+4."
            )

        return value


    @field_validator("city")
    @classmethod
    def validate_city(cls, value):
        value = value.strip()

        if not 1 <= len(value) <= 100:
            raise ValueError(
                "City must be between 1 and 100 characters."
            )

        return value


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class PatientRead(PatientBase):

    model_config = ConfigDict(
        from_attributes=True
    )

    patient_id: UUID
    created_at: str | object
    updated_at: str | object
    deleted_at: Optional[str | object] = None