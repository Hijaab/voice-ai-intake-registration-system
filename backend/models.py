from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Patient(SQLModel, table=True):
    __tablename__ = "patients"

    patient_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
    )

    # Required demographic information
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)

    date_of_birth: date

    sex: str = Field(max_length=30)

    phone_number: str = Field(
        max_length=10,
        index=True,
    )

    # Optional
    email: Optional[str] = Field(
        default=None,
        max_length=254,
    )

    address_line_1: str = Field(max_length=200)

    address_line_2: Optional[str] = Field(
        default=None,
        max_length=200,
    )

    city: str = Field(max_length=100)

    state: str = Field(
        max_length=2,
        index=True,
    )

    zip_code: str = Field(max_length=10)

    insurance_provider: Optional[str] = Field(
        default=None,
        max_length=150,
    )

    insurance_member_id: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    preferred_language: str = Field(
        default="English",
        max_length=50,
    )

    emergency_contact_name: Optional[str] = Field(
        default=None,
        max_length=150,
    )

    emergency_contact_phone: Optional[str] = Field(
        default=None,
        max_length=10,
    )

    # System fields
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    deleted_at: Optional[datetime] = Field(
        default=None
    )