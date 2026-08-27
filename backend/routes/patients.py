import logging
from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from ..crud import (
    create_patient,
    get_patient,
    get_patients,
    soft_delete_patient,
    update_patient,
)
from ..schemas import (
    PatientCreate,
    PatientUpdate,
    normalize_phone,
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

logger = logging.getLogger(__name__)


def success(data):
    return {
        "data": data,
        "error": None,
    }


def failure(message):
    return {
        "data": None,
        "error": message,
    }


@router.get("")
def list_patients(
    last_name: str | None = Query(
        default=None
    ),

    date_of_birth: date | None = Query(
        default=None
    ),

    phone_number: str | None = Query(
        default=None
    ),
):

    normalized_phone = None

    if phone_number:
        try:
            normalized_phone = normalize_phone(
                phone_number
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=str(exc)
            )

    patients = get_patients(
        last_name=last_name,
        date_of_birth=date_of_birth,
        phone_number=normalized_phone,
    )

    return success(patients)


@router.get("/{patient_id}")
def retrieve_patient(
    patient_id: UUID
):

    patient = get_patient(patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found."
        )

    return success(patient)


@router.post(
    "",
    status_code=201
)
def create_new_patient(
    patient_data: PatientCreate
):

    try:

        patient = create_patient(
            patient_data
        )

        logger.info(
            "PATIENT_CREATED patient_id=%s data=%s",
            patient.patient_id,
            patient_data.model_dump(
                mode="json"
            ),
        )

        return success(patient)

    except Exception as exc:

        logger.exception(
            "Failed to create patient"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create patient."
        ) from exc


@router.put("/{patient_id}")
def update_existing_patient(
    patient_id: UUID,
    patient_data: PatientUpdate
):

    patient = get_patient(patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found."
        )

    try:

        updated = update_patient(
            patient,
            patient_data
        )

        return success(updated)

    except Exception as exc:

        logger.exception(
            "Failed to update patient"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to update patient."
        ) from exc


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: UUID
):

    patient = get_patient(patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found."
        )

    try:

        deleted = soft_delete_patient(
            patient
        )

        return success({
            "patient_id": str(
                deleted.patient_id
            ),
            "deleted": True,
        })

    except Exception as exc:

        logger.exception(
            "Failed to delete patient"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete patient."
        ) from exc