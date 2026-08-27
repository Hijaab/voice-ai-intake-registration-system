import os
import re
from datetime import datetime, date
from typing import Optional
from uuid import UUID, uuid4

import streamlit as st
from sqlmodel import Field, SQLModel, Session, create_engine, select
from pydantic import BaseModel, EmailStr, field_validator


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="Voice AI - Patient Registration",
    page_icon="🎙️",
    layout="wide",
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./patients.db"
)

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)


# ============================================================
# CONSTANTS
# ============================================================

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE",
    "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
    "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
    "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY",
}

VALID_SEX = {
    "Male",
    "Female",
    "Other",
    "Decline To Answer",
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def utc_now() -> str:
    """
    Return current UTC time as ISO 8601 string.
    """
    return datetime.utcnow().isoformat()


def sanitize_phone(phone: str) -> str:
    """
    Convert phone number to 10-digit US format.

    Examples:
        (555) 123-4567 -> 5551234567
        +1 555 123 4567 -> 5551234567
    """

    if not phone:
        return ""

    cleaned = re.sub(r"\D", "", str(phone))

    if len(cleaned) == 11 and cleaned.startswith("1"):
        cleaned = cleaned[1:]

    return cleaned


# ============================================================
# DATABASE MODEL
# ============================================================

class Patient(SQLModel, table=True):

    __tablename__ = "patients"

    patient_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
    )

    first_name: str = Field(
        nullable=False
    )

    last_name: str = Field(
        nullable=False
    )

    date_of_birth: str = Field(
        nullable=False
    )

    sex: str = Field(
        nullable=False
    )

    phone_number: str = Field(
        nullable=False,
        index=True,
    )

    email: Optional[str] = Field(
        default=None
    )

    address_line_1: str = Field(
        nullable=False
    )

    address_line_2: Optional[str] = Field(
        default=None
    )

    city: str = Field(
        nullable=False
    )

    state: str = Field(
        nullable=False
    )

    zip_code: str = Field(
        nullable=False
    )

    insurance_provider: Optional[str] = Field(
        default=None
    )

    insurance_member_id: Optional[str] = Field(
        default=None
    )

    preferred_language: str = Field(
        default="English"
    )

    emergency_contact_name: Optional[str] = Field(
        default=None
    )

    emergency_contact_phone: Optional[str] = Field(
        default=None
    )

    created_at: str = Field(
        default_factory=utc_now
    )

    updated_at: str = Field(
        default_factory=utc_now
    )

    deleted_at: Optional[str] = Field(
        default=None,
        index=True,
    )


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def initialize_database():
    SQLModel.metadata.create_all(engine)


initialize_database()


# ============================================================
# PYDANTIC VALIDATION SCHEMA
# ============================================================

class PatientBaseSchema(BaseModel):

    first_name: str
    last_name: str

    date_of_birth: str

    sex: str

    phone_number: str

    email: Optional[EmailStr] = None

    address_line_1: str

    address_line_2: Optional[str] = None

    city: str

    state: str

    zip_code: str

    insurance_provider: Optional[str] = None

    insurance_member_id: Optional[str] = None

    preferred_language: Optional[str] = "English"

    emergency_contact_name: Optional[str] = None

    emergency_contact_phone: Optional[str] = None


    # --------------------------------------------------------
    # NAME VALIDATION
    # --------------------------------------------------------

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str) -> str:

        value = value.strip()

        if not (1 <= len(value) <= 50):
            raise ValueError(
                "Name must contain between 1 and 50 characters."
            )

        if not re.match(
            r"^[A-Za-z\s'\-]+$",
            value
        ):
            raise ValueError(
                "Name may contain only letters, spaces, apostrophes and hyphens."
            )

        return value


    # --------------------------------------------------------
    # DATE OF BIRTH VALIDATION
    # --------------------------------------------------------

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: str) -> str:

        value = value.strip()

        try:
            dob_date = datetime.strptime(
                value,
                "%m/%d/%Y"
            ).date()

        except ValueError:
            raise ValueError(
                "Date of birth must use MM/DD/YYYY format."
            )

        if dob_date > date.today():
            raise ValueError(
                "Date of birth cannot be in the future."
            )

        return value


    # --------------------------------------------------------
    # SEX VALIDATION
    # --------------------------------------------------------

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, value: str) -> str:

        value = value.strip()

        normalized = value.title()

        # Handle "Decline to Answer"
        if normalized.lower() == "decline to answer":
            normalized = "Decline To Answer"

        if normalized not in VALID_SEX:
            raise ValueError(
                "Sex must be one of: "
                + ", ".join(sorted(VALID_SEX))
            )

        return normalized


    # --------------------------------------------------------
    # PHONE VALIDATION
    # --------------------------------------------------------

    @field_validator(
        "phone_number",
        "emergency_contact_phone"
    )
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:

        if value is None:
            return None

        cleaned = sanitize_phone(value)

        if len(cleaned) != 10:
            raise ValueError(
                "Phone number must be a valid 10-digit US phone number."
            )

        return cleaned


    # --------------------------------------------------------
    # STATE VALIDATION
    # --------------------------------------------------------

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str) -> str:

        value = value.strip().upper()

        if value not in US_STATES:
            raise ValueError(
                "State must be a valid 2-letter US state abbreviation."
            )

        return value


    # --------------------------------------------------------
    # ZIP CODE VALIDATION
    # --------------------------------------------------------

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, value: str) -> str:

        value = value.strip()

        if not re.match(
            r"^\d{5}(-\d{4})?$",
            value
        ):
            raise ValueError(
                "ZIP code must be 5 digits or ZIP+4 format."
            )

        return value


class PatientCreateSchema(PatientBaseSchema):
    pass


class PatientUpdateSchema(BaseModel):

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
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


# ============================================================
# DATABASE SERIALIZATION
# ============================================================

def patient_to_dict(patient: Patient) -> dict:

    return {
        "patient_id": str(patient.patient_id),
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "date_of_birth": patient.date_of_birth,
        "sex": patient.sex,
        "phone_number": patient.phone_number,
        "email": patient.email,
        "address_line_1": patient.address_line_1,
        "address_line_2": patient.address_line_2,
        "city": patient.city,
        "state": patient.state,
        "zip_code": patient.zip_code,
        "insurance_provider": patient.insurance_provider,
        "insurance_member_id": patient.insurance_member_id,
        "preferred_language": patient.preferred_language,
        "emergency_contact_name": patient.emergency_contact_name,
        "emergency_contact_phone": patient.emergency_contact_phone,
        "created_at": patient.created_at,
        "updated_at": patient.updated_at,
        "deleted_at": patient.deleted_at,
    }


# ============================================================
# DATABASE OPERATIONS
# ============================================================

def get_active_patients():

    with Session(engine) as session:

        statement = (
            select(Patient)
            .where(Patient.deleted_at == None)
            .order_by(Patient.created_at.desc())
        )

        return session.exec(statement).all()


def create_patient(payload: PatientCreateSchema):

    data = payload.model_dump()

    patient = Patient(**data)

    with Session(engine) as session:

        session.add(patient)

        session.commit()

        session.refresh(patient)

        return patient


def find_patient_by_phone(phone_number: str):

    phone = sanitize_phone(phone_number)

    if not phone:
        return None

    with Session(engine) as session:

        statement = (
            select(Patient)
            .where(
                Patient.phone_number == phone,
                Patient.deleted_at == None,
            )
        )

        return session.exec(statement).first()


def find_patient(patient_id: UUID):

    with Session(engine) as session:

        patient = session.get(
            Patient,
            patient_id
        )

        if not patient:
            return None

        if patient.deleted_at:
            return None

        return patient


def soft_delete_patient(patient_id: UUID):

    with Session(engine) as session:

        patient = session.get(
            Patient,
            patient_id
        )

        if not patient or patient.deleted_at:
            return False

        patient.deleted_at = utc_now()
        patient.updated_at = utc_now()

        session.add(patient)

        session.commit()

        return True


# ============================================================
# STREAMLIT HEADER
# ============================================================

st.title(
    "🎙️ Voice AI - Patient Registration Dashboard"
)

st.caption(
    "Patient registration and Vapi integration dashboard"
)


# ============================================================
# SYSTEM STATUS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.success(
        "✅ Streamlit application is running"
    )

with col2:

    st.success(
        "✅ Database initialized"
    )

with col3:

    st.info(
        "ℹ️ FastAPI runs separately"
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select page",
    [
        "Dashboard",
        "Register Patient",
        "Search Patient",
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.subheader(
        "Registered Patients"
    )

    patients = get_active_patients()

    if patients:

        rows = [
            patient_to_dict(patient)
            for patient in patients
        ]

        st.dataframe(
            rows,
            use_container_width=True,
        )

        st.metric(
            "Active Patients",
            len(patients)
        )

    else:

        st.info(
            "No active patient records found."
        )


# ============================================================
# REGISTER PATIENT
# ============================================================

elif page == "Register Patient":

    st.subheader(
        "Register New Patient"
    )

    with st.form("patient_registration_form"):

        col1, col2 = st.columns(2)

        with col1:

            first_name = st.text_input(
                "First Name *"
            )

            last_name = st.text_input(
                "Last Name *"
            )

            date_of_birth = st.text_input(
                "Date of Birth *",
                placeholder="MM/DD/YYYY"
            )

            sex = st.selectbox(
                "Sex *",
                [
                    "Male",
                    "Female",
                    "Other",
                    "Decline To Answer",
                ]
            )

            phone_number = st.text_input(
                "Phone Number *",
                placeholder="555-123-4567"
            )

            email = st.text_input(
                "Email"
            )

        with col2:

            address_line_1 = st.text_input(
                "Address Line 1 *"
            )

            address_line_2 = st.text_input(
                "Address Line 2"
            )

            city = st.text_input(
                "City *"
            )

            state = st.text_input(
                "State *",
                placeholder="CA"
            )

            zip_code = st.text_input(
                "ZIP Code *",
                placeholder="90210"
            )

            preferred_language = st.text_input(
                "Preferred Language",
                value="English"
            )

        st.markdown(
            "### Insurance"
        )

        col1, col2 = st.columns(2)

        with col1:

            insurance_provider = st.text_input(
                "Insurance Provider"
            )

        with col2:

            insurance_member_id = st.text_input(
                "Insurance Member ID"
            )

        st.markdown(
            "### Emergency Contact"
        )

        col1, col2 = st.columns(2)

        with col1:

            emergency_contact_name = st.text_input(
                "Emergency Contact Name"
            )

        with col2:

            emergency_contact_phone = st.text_input(
                "Emergency Contact Phone"
            )

        submitted = st.form_submit_button(
            "Register Patient",
            type="primary",
        )

        if submitted:

            try:

                payload = PatientCreateSchema(
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=date_of_birth,
                    sex=sex,
                    phone_number=phone_number,
                    email=email or None,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2 or None,
                    city=city,
                    state=state,
                    zip_code=zip_code,
                    insurance_provider=(
                        insurance_provider or None
                    ),
                    insurance_member_id=(
                        insurance_member_id or None
                    ),
                    preferred_language=(
                        preferred_language or "English"
                    ),
                    emergency_contact_name=(
                        emergency_contact_name or None
                    ),
                    emergency_contact_phone=(
                        emergency_contact_phone or None
                    ),
                )

                # Check duplicate phone
                existing = find_patient_by_phone(
                    payload.phone_number
                )

                if existing:

                    st.error(
                        "A patient with this phone number "
                        "already exists."
                    )

                else:

                    patient = create_patient(
                        payload
                    )

                    st.success(
                        "Patient registered successfully!"
                    )

                    st.json(
                        patient_to_dict(patient)
                    )

            except Exception as exc:

                st.error(
                    f"Registration failed: {exc}"
                )


# ============================================================
# SEARCH PATIENT
# ============================================================

elif page == "Search Patient":

    st.subheader(
        "Search Patient"
    )

    search_phone = st.text_input(
        "Phone Number"
    )

    search_last_name = st.text_input(
        "Last Name"
    )

    if st.button(
        "Search",
        type="primary"
    ):

        results = []

        with Session(engine) as session:

            statement = (
                select(Patient)
                .where(
                    Patient.deleted_at == None
                )
            )

            if search_phone:

                phone = sanitize_phone(
                    search_phone
                )

                statement = statement.where(
                    Patient.phone_number == phone
                )

            if search_last_name:

                statement = statement.where(
                    Patient.last_name.ilike(
                        f"%{search_last_name.strip()}%"
                    )
                )

            results = session.exec(
                statement
            ).all()

        if results:

            st.success(
                f"Found {len(results)} patient(s)."
            )

            for patient in results:

                with st.expander(
                    f"{patient.first_name} "
                    f"{patient.last_name} "
                    f"— {patient.phone_number}"
                ):

                    st.json(
                        patient_to_dict(patient)
                    )

        else:

            st.warning(
                "No patient found."
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Voice AI Patient Registration System"
)

st.caption(
    "Dashboard is running on Streamlit Cloud."
)