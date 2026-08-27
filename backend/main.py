from datetime import datetime, timezone
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query
from sqlmodel import select

from backend.database import create_db_and_tables, get_session
from backend.models import Patient
from backend.schemas import PatientCreate, PatientUpdate
from backend.validation import (
    normalize_phone,
    validate_date_of_birth,
    validate_name,
    validate_optional_phone,
    validate_state,
    validate_zip,
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Voice AI Patient Registration API",
    description=(
        "REST API for the Voice AI Patient Registration "
        "Technical Assessment."
    ),
    version="1.0.0",
)


# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
def startup():

    create_db_and_tables()


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "data": {
            "status": "ok"
        },
        "error": None,
    }


# =========================================================
# CREATE PATIENT
# =========================================================

@app.post(
    "/patients",
    status_code=201,
)
def create_patient(
    patient_data: PatientCreate,
):

    try:

        first_name = validate_name(
            patient_data.first_name,
            "First name",
        )

        last_name = validate_name(
            patient_data.last_name,
            "Last name",
        )

        date_of_birth = validate_date_of_birth(
            patient_data.date_of_birth
        )

        phone_number = normalize_phone(
            patient_data.phone_number
        )

        state = validate_state(
            patient_data.state
        )

        zip_code = validate_zip(
            patient_data.zip_code
        )

        emergency_phone = validate_optional_phone(
            patient_data.emergency_contact_phone
        )

        # -------------------------------------------------
        # CHECK DUPLICATE PHONE
        # -------------------------------------------------

        with get_session() as session:

            existing = session.exec(
                select(Patient)
                .where(
                    Patient.phone_number == phone_number,
                    Patient.deleted_at.is_(None),
                )
            ).first()

            if existing:

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "A patient with this phone number "
                        "already exists."
                    ),
                )

            # -------------------------------------------------
            # CREATE PATIENT
            # -------------------------------------------------

            patient = Patient(
                first_name=first_name,
                last_name=last_name,

                date_of_birth=date_of_birth,

                sex=patient_data.sex,

                phone_number=phone_number,

                email=(
                    str(patient_data.email)
                    if patient_data.email
                    else None
                ),

                address_line_1=(
                    patient_data.address_line_1.strip()
                ),

                address_line_2=(
                    patient_data.address_line_2.strip()
                    if patient_data.address_line_2
                    else None
                ),

                city=patient_data.city.strip(),

                state=state,

                zip_code=zip_code,

                insurance_provider=(
                    patient_data.insurance_provider.strip()
                    if patient_data.insurance_provider
                    else None
                ),

                insurance_member_id=(
                    patient_data.insurance_member_id.strip()
                    if patient_data.insurance_member_id
                    else None
                ),

                preferred_language=(
                    patient_data.preferred_language.strip()
                    or "English"
                ),

                emergency_contact_name=(
                    patient_data.emergency_contact_name.strip()
                    if patient_data.emergency_contact_name
                    else None
                ),

                emergency_contact_phone=emergency_phone,
            )

            session.add(patient)

            session.commit()

            session.refresh(patient)

            # -------------------------------------------------
            # OBSERVABILITY
            # -------------------------------------------------

            print(
                "PATIENT_REGISTERED",
                {
                    "patient_id": str(patient.patient_id),
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                    "phone_number": patient.phone_number,
                },
            )

            return {
                "data": patient,
                "error": None,
            }

    except HTTPException:
        raise

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except Exception as exc:

        print(
            "PATIENT_CREATE_ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create patient.",
        )


# =========================================================
# LIST PATIENTS
# =========================================================

@app.get("/patients")
def list_patients(
    last_name: str | None = Query(
        default=None
    ),

    date_of_birth: str | None = Query(
        default=None
    ),

    phone_number: str | None = Query(
        default=None
    ),
):

    try:

        with get_session() as session:

            statement = select(Patient).where(
                Patient.deleted_at.is_(None)
            )

            # ---------------------------------------------
            # LAST NAME FILTER
            # ---------------------------------------------

            if last_name:

                statement = statement.where(
                    Patient.last_name.ilike(
                        last_name.strip()
                    )
                )

            # ---------------------------------------------
            # DATE OF BIRTH FILTER
            # ---------------------------------------------

            if date_of_birth:

                from datetime import date

                try:

                    parsed_date = date.fromisoformat(
                        date_of_birth
                    )

                except ValueError:

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "date_of_birth must use "
                            "YYYY-MM-DD format."
                        ),
                    )

                statement = statement.where(
                    Patient.date_of_birth == parsed_date
                )

            # ---------------------------------------------
            # PHONE FILTER
            # ---------------------------------------------

            if phone_number:

                try:

                    normalized = normalize_phone(
                        phone_number
                    )

                except ValueError as exc:

                    raise HTTPException(
                        status_code=400,
                        detail=str(exc),
                    )

                statement = statement.where(
                    Patient.phone_number == normalized
                )

            patients = session.exec(
                statement
            ).all()

            return {
                "data": patients,
                "error": None,
            }

    except HTTPException:
        raise

    except Exception as exc:

        print(
            "PATIENT_LIST_ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve patients.",
        )


# =========================================================
# GET SINGLE PATIENT
# =========================================================

@app.get("/patients/{patient_id}")
def get_patient(
    patient_id: UUID,
):

    with get_session() as session:

        patient = session.exec(
            select(Patient)
            .where(
                Patient.patient_id == patient_id,
                Patient.deleted_at.is_(None),
            )
        ).first()

        if not patient:

            raise HTTPException(
                status_code=404,
                detail="Patient not found.",
            )

        return {
            "data": patient,
            "error": None,
        }


# =========================================================
# UPDATE PATIENT
# =========================================================

@app.put("/patients/{patient_id}")
def update_patient(
    patient_id: UUID,
    patient_data: PatientUpdate,
):

    try:

        with get_session() as session:

            patient = session.exec(
                select(Patient)
                .where(
                    Patient.patient_id == patient_id,
                    Patient.deleted_at.is_(None),
                )
            ).first()

            if not patient:

                raise HTTPException(
                    status_code=404,
                    detail="Patient not found.",
                )

            updates = patient_data.model_dump(
                exclude_unset=True
            )

            # ---------------------------------------------
            # VALIDATE INDIVIDUAL FIELDS
            # ---------------------------------------------

            if "first_name" in updates:

                patient.first_name = validate_name(
                    updates["first_name"],
                    "First name",
                )

            if "last_name" in updates:

                patient.last_name = validate_name(
                    updates["last_name"],
                    "Last name",
                )

            if "date_of_birth" in updates:

                patient.date_of_birth = (
                    validate_date_of_birth(
                        updates["date_of_birth"]
                    )
                )

            if "phone_number" in updates:

                patient.phone_number = normalize_phone(
                    updates["phone_number"]
                )

            if "state" in updates:

                patient.state = validate_state(
                    updates["state"]
                )

            if "zip_code" in updates:

                patient.zip_code = validate_zip(
                    updates["zip_code"]
                )

            if "emergency_contact_phone" in updates:

                patient.emergency_contact_phone = (
                    validate_optional_phone(
                        updates["emergency_contact_phone"]
                    )
                )

            # ---------------------------------------------
            # OTHER FIELDS
            # ---------------------------------------------

            simple_fields = [
                "email",
                "address_line_1",
                "address_line_2",
                "city",
                "insurance_provider",
                "insurance_member_id",
                "preferred_language",
                "emergency_contact_name",
                "sex",
            ]

            for field in simple_fields:

                if field in updates:

                    value = updates[field]

                    if isinstance(value, str):

                        value = value.strip()

                    if field == "email" and value:

                        value = str(value)

                    setattr(
                        patient,
                        field,
                        value,
                    )

            patient.updated_at = datetime.now(
                timezone.utc
            )

            session.add(patient)

            session.commit()

            session.refresh(patient)

            print(
                "PATIENT_UPDATED",
                str(patient.patient_id),
            )

            return {
                "data": patient,
                "error": None,
            }

    except HTTPException:
        raise

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except Exception as exc:

        print(
            "PATIENT_UPDATE_ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to update patient.",
        )


# =========================================================
# SOFT DELETE
# =========================================================

@app.delete("/patients/{patient_id}")
def delete_patient(
    patient_id: UUID,
):

    with get_session() as session:

        patient = session.exec(
            select(Patient)
            .where(
                Patient.patient_id == patient_id,
                Patient.deleted_at.is_(None),
            )
        ).first()

        if not patient:

            raise HTTPException(
                status_code=404,
                detail="Patient not found.",
            )

        now = datetime.now(
            timezone.utc
        )

        patient.deleted_at = now

        patient.updated_at = now

        session.add(patient)

        session.commit()

        return {
            "data": {
                "patient_id": str(
                    patient.patient_id
                ),
                "deleted": True,
            },
            "error": None,
        }