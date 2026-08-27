from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from backend.models import Sex


# =========================================================
# CREATE PATIENT
# =========================================================

class PatientCreate(BaseModel):

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

    phone_number: str

    email: Optional[EmailStr] = None

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

    zip_code: str

    insurance_provider: Optional[str] = None

    insurance_member_id: Optional[str] = None

    preferred_language: str = "English"

    emergency_contact_name: Optional[str] = None

    emergency_contact_phone: Optional[str] = None


# =========================================================
# UPDATE PATIENT
# =========================================================

class PatientUpdate(BaseModel):

    first_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    last_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    date_of_birth: Optional[date] = None

    sex: Optional[Sex] = None

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


# =========================================================
# RESPONSE
# =========================================================

class PatientResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    patient_id: UUID

    first_name: str

    last_name: str

    date_of_birth: date

    sex: Sex

    phone_number: str

    email: Optional[EmailStr]

    address_line_1: str

    address_line_2: Optional[str]

    city: str

    state: str

    zip_code: str

    insurance_provider: Optional[str]

    insurance_member_id: Optional[str]

    preferred_language: str

    emergency_contact_name: Optional[str]

    emergency_contact_phone: Optional[str]

    created_at: datetime

    updated_at: datetime

    deleted_at: Optional[datetime]


# =========================================================
# API ENVELOPE
# =========================================================

class ErrorResponse(BaseModel):

    message: str


class APIResponse(BaseModel):

    data: object | None = None

    error: object | None = None