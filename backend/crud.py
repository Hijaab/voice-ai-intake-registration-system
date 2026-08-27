from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlmodel import select

from .database import get_session
from .models import Patient
from .schemas import PatientCreate, PatientUpdate


def create_patient(data: PatientCreate) -> Patient:

    patient = Patient(
        **data.model_dump()
    )

    with get_session() as session:

        session.add(patient)
        session.commit()
        session.refresh(patient)

        return patient


def get_patient(
    patient_id: UUID
) -> Optional[Patient]:

    with get_session() as session:

        statement = select(Patient).where(
            Patient.patient_id == patient_id,
            Patient.deleted_at.is_(None),
        )

        return session.exec(statement).first()


def get_patients(
    last_name: Optional[str] = None,
    date_of_birth=None,
    phone_number: Optional[str] = None,
):

    with get_session() as session:

        statement = select(Patient).where(
            Patient.deleted_at.is_(None)
        )

        if last_name:
            statement = statement.where(
                Patient.last_name.ilike(
                    last_name.strip()
                )
            )

        if date_of_birth:
            statement = statement.where(
                Patient.date_of_birth == date_of_birth
            )

        if phone_number:
            statement = statement.where(
                Patient.phone_number == phone_number
            )

        statement = statement.order_by(
            Patient.created_at.desc()
        )

        return session.exec(statement).all()


def update_patient(
    patient: Patient,
    data: PatientUpdate
):

    updates = data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(patient, key, value)

    patient.updated_at = datetime.now(timezone.utc)

    with get_session() as session:

        session.add(patient)
        session.commit()
        session.refresh(patient)

        return patient


def soft_delete_patient(
    patient: Patient
):

    patient.deleted_at = datetime.now(timezone.utc)
    patient.updated_at = datetime.now(timezone.utc)

    with get_session() as session:

        session.add(patient)
        session.commit()
        session.refresh(patient)

        return patient