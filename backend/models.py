from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Sex(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    DECLINE = "Decline to Answer"


class Patient(SQLModel, table=True):
    __tablename__ = "patients"

    # ---------------------------------------------------------
    # PRIMARY KEY
    # ---------------------------------------------------------

    patient_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
    )

    # ---------------------------------------------------------
    # REQUIRED DEMOGRAPHIC INFORMATION
    # ---------------------------------------------------------

    first_name: str = Field(
        min_length=1,
        max_length=50,
    )

    last_name: str = Field(
        min_length=1,
        max_length=50,
    )

    date_of_birth: date

    sex: Sex

    phone_number: str = Field(
        min_length=10,
        max_length=10,
        index=True,
    )

    # ---------------------------------------------------------
    # OPTIONAL CONTACT INFORMATION
    # ---------------------------------------------------------

    email: Optional[str] = None

    # ---------------------------------------------------------
    # ADDRESS
    # ---------------------------------------------------------

    address_line_1: str = Field(
        min_length=1,
    )

    address_line_2: Optional[str] = None

    city: str = Field(
        min_length=1,
        max_length=100,
    )

    state: str = Field(
        min_length=2,
        max_length=2,
    )

    zip_code: str = Field(
        min_length=5,
        max_length=10,
    )

    # ---------------------------------------------------------
    # INSURANCE
    # ---------------------------------------------------------

    insurance_provider: Optional[str] = None

    insurance_member_id: Optional[str] = None

    # ---------------------------------------------------------
    # PREFERENCES
    # ---------------------------------------------------------

    preferred_language: str = "English"

    # ---------------------------------------------------------
    # EMERGENCY CONTACT
    # ---------------------------------------------------------

    emergency_contact_name: Optional[str] = None

    emergency_contact_phone: Optional[str] = None

    # ---------------------------------------------------------
    # SYSTEM TIMESTAMPS
    # ---------------------------------------------------------

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # ---------------------------------------------------------
    # SOFT DELETE
    # ---------------------------------------------------------

    deleted_at: Optional[datetime] = None