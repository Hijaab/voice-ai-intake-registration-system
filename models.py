from typing import Optional

from sqlmodel import SQLModel, Field


# ============================================================
# PATIENT DATABASE MODEL
# ============================================================

class Patient(SQLModel, table=True):

    __tablename__ = "patients"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    # --------------------------------------------------------
    # PERSONAL INFORMATION
    # --------------------------------------------------------

    first_name: str
    last_name: str

    date_of_birth: Optional[str] = None

    gender: Optional[str] = None

    phone: Optional[str] = None

    email: Optional[str] = None

    address: Optional[str] = None

    city: Optional[str] = None

    postal_code: Optional[str] = None

    country: Optional[str] = None

    # --------------------------------------------------------
    # MEDICAL INFORMATION
    # --------------------------------------------------------

    symptoms: Optional[str] = None

    medical_history: Optional[str] = None

    current_medications: Optional[str] = None

    allergies: Optional[str] = None

    emergency_contact: Optional[str] = None

    emergency_phone: Optional[str] = None

    # --------------------------------------------------------
    # VOICE / AI INFORMATION
    # --------------------------------------------------------

    transcript: Optional[str] = None

    ai_summary: Optional[str] = None

    ai_recommendation: Optional[str] = None

    # --------------------------------------------------------
    # SYSTEM INFORMATION
    # --------------------------------------------------------

    created_at: Optional[str] = None