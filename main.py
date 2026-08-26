import os
import re
import threading
import uvicorn
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4

import streamlit as st
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, validator
from sqlmodel import Field, SQLModel, Session, create_engine, select

# --- Persistent SQLite configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./patients.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


# --- Database Model ---
class Patient(SQLModel, table=True):
    __tablename__ = "patients"

    patient_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    date_of_birth: str = Field(nullable=False)
    sex: str = Field(nullable=False)
    phone_number: str = Field(nullable=False, index=True)
    email: Optional[str] = Field(default=None)
    address_line_1: str = Field(nullable=False)
    address_line_2: Optional[str] = Field(default=None)
    city: str = Field(nullable=False)
    state: str = Field(nullable=False)
    zip_code: str = Field(nullable=False)
    insurance_provider: Optional[str] = Field(default=None)
    insurance_member_id: Optional[str] = Field(default=None)
    preferred_language: str = Field(default="English")
    emergency_contact_name: Optional[str] = Field(default=None)
    emergency_contact_phone: Optional[str] = Field(default=None)

    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    deleted_at: Optional[str] = Field(default=None, index=True)


US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
}
VALID_SEX = {"Male", "Female", "Other", "Decline to Answer"}


def sanitize_phone(phone: str) -> str:
    cleaned = re.sub(r"\D", "", phone)
    if len(cleaned) == 11 and cleaned.startswith("1"):
        cleaned = cleaned[1:]
    return cleaned


# --- Pydantic Schemas ---
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

    @validator("first_name", "last_name")
    def validate_name(cls, v):
        v = v.strip()
        if not (1 <= len(v) <= 50) or not re.match(r"^[A-Za-z\s'\-]+$", v):
            raise ValueError("Name must be 1-50 alphabetic characters")
        return v

    @validator("date_of_birth")
    def validate_dob(cls, v):
        v = v.strip()
        try:
            dob_date = datetime.strptime(v, "%m/%d/%Y").date()
        except ValueError:
            raise ValueError("Date of birth must be MM/DD/YYYY")
        if dob_date > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v

    @validator("sex")
    def validate_sex(cls, v):
        v = v.strip().title()
        if v not in VALID_SEX:
            raise ValueError(f"Sex must be one of: {', '.join(VALID_SEX)}")
        return v

    @validator("phone_number", "emergency_contact_phone")
    def validate_phone(cls, v):
        if v is None:
            return v
        cleaned = sanitize_phone(v)
        if len(cleaned) != 10:
            raise ValueError("Must be valid 10-digit U.S. phone number")
        return cleaned

    @validator("state")
    def validate_state(cls, v):
        v = v.strip().upper()
        if v not in US_STATES:
            raise ValueError("Must be valid 2-letter U.S. state abbreviation")
        return v

    @validator("zip_code")
    def validate_zip(cls, v):
        v = v.strip()
        if not re.match(r"^\d{5}(-\d{4})?$", v):
            raise ValueError("ZIP code must be 5 digits or ZIP+4 format")
        return v


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


# --- FastAPI Application ---
app = FastAPI(title="CareCloud Voice AI - Patient Registration API")


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# Required Streamlit Cloud Health Check Endpoint
@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/patients")
def list_patients(
    last_name: Optional[str] = Query(None),
    date_of_birth: Optional[str] = Query(None),
    phone_number: Optional[str] = Query(None)
):
    with Session(engine) as session:
        query = select(Patient).where(Patient.deleted_at == None)
        if last_name:
            query = query.where(Patient.last_name.ilike(f"%{last_name.strip()}%"))
        if date_of_birth:
            query = query.where(Patient.date_of_birth == date_of_birth.strip())
        if phone_number:
            cleaned = sanitize_phone(phone_number)
            query = query.where(Patient.phone_number == cleaned)
        patients = session.exec(query).all()
        return {"data": [p.dict() for p in patients], "error": None}


@app.get("/patients/{patient_id}")
def get_patient(patient_id: UUID):
    with Session(engine) as session:
        patient = session.get(Patient, patient_id)
        if not patient or patient.deleted_at:
            raise HTTPException(status_code=404, detail="Patient not found")
        return {"data": patient.dict(), "error": None}


@app.post("/patients", status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreateSchema):
    with Session(engine) as session:
        patient = Patient(**payload.dict())
        session.add(patient)
        session.commit()
        session.refresh(patient)
        return {"data": patient.dict(), "error": None}


@app.put("/patients/{patient_id}")
def update_patient(patient_id: UUID, payload: PatientUpdateSchema):
    with Session(engine) as session:
        patient = session.get(Patient, patient_id)
        if not patient or patient.deleted_at:
            raise HTTPException(status_code=404, detail="Patient not found")
        for k, v in payload.dict(exclude_unset=True).items():
            if v is not None:
                setattr(patient, k, v)
        patient.updated_at = datetime.utcnow().isoformat()
        session.add(patient)
        session.commit()
        session.refresh(patient)
        return {"data": patient.dict(), "error": None}


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: UUID):
    with Session(engine) as session:
        patient = session.get(Patient, patient_id)
        if not patient or patient.deleted_at:
            raise HTTPException(status_code=404, detail="Patient not found")
        patient.deleted_at = datetime.utcnow().isoformat()
        session.add(patient)
        session.commit()
        return {"data": {"message": f"Patient {patient_id} soft-deleted"}, "error": None}


@app.post("/vapi/webhook")
async def vapi_webhook(payload: dict):
    message_type = payload.get("message", {}).get("type")
    if message_type == "tool-calls":
        for tool_call in payload.get("message", {}).get("toolCalls", []):
            tool_name = tool_call.get("function", {}).get("name")
            args = tool_call.get("function", {}).get("arguments", {})
            call_id = tool_call.get("id")

            if tool_name == "lookup_patient":
                phone = sanitize_phone(args.get("phone_number", ""))
                with Session(engine) as session:
                    query = select(Patient).where(Patient.phone_number == phone, Patient.deleted_at == None)
                    existing = session.exec(query).first()
                    res = (
                        {
                            "found": True,
                            "patient_id": str(existing.patient_id),
                            "first_name": existing.first_name,
                            "last_name": existing.last_name,
                        }
                        if existing
                        else {"found": False}
                    )
                    return {"results": [{"toolCallId": call_id, "result": res}]}

            elif tool_name == "register_patient":
                try:
                    schema = PatientCreateSchema(**args)
                    with Session(engine) as session:
                        patient = Patient(**schema.dict())
                        session.add(patient)
                        session.commit()
                        session.refresh(patient)
                        return {
                            "results": [
                                {
                                    "toolCallId": call_id,
                                    "result": {"success": True, "patient_id": str(patient.patient_id)},
                                }
                            ]
                        }
                except Exception as e:
                    return {"results": [{"toolCallId": call_id, "result": {"success": False, "error": str(e)}}]}
    return {"status": "ok"}


# --- Start FastAPI Background Thread ---
def start_fastapi_thread():
    SQLModel.metadata.create_all(engine)
    # Bind to localhost on internal port 8000 to prevent port-grabbing
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if "fastapi_started" not in st.session_state:
    thread = threading.Thread(target=start_fastapi_thread, daemon=True)
    thread.start()
    st.session_state["fastapi_started"] = True


# --- Streamlit Front-End UI ---
st.set_page_config(page_title="CareCloud Voice AI", page_icon="🎙️", layout="wide")
st.title("CareCloud Voice AI - Patient Registration Dashboard")
st.success("FastAPI & Vapi Webhook Engine is active internally on port 8000.")

st.subheader("Registered Patients")
with Session(engine) as session:
    patients = session.exec(select(Patient).where(Patient.deleted_at == None)).all()
    if patients:
        st.dataframe([p.dict() for p in patients], use_container_width=True)
    else:
        st.info("No active patient records found in database.")

st.json({"status": "healthy", "service": "FastAPI + Streamlit"})