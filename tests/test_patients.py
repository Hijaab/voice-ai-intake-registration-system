from fastapi.testclient import TestClient

from main.app import app


client = TestClient(app)


# ============================================================
# TEST DATA
# ============================================================

def valid_patient():
    """
    Returns a complete valid patient payload.

    This payload follows the demographic requirements
    specified in the technical assessment.
    """

    return {
        "first_name": "Jane",
        "last_name": "Doe",
        "date_of_birth": "1995-03-15",
        "sex": "Female",

        "phone_number": "415-555-1234",
        "email": "jane@example.com",

        "address_line_1": "123 Main Street",
        "address_line_2": "Apt 4B",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94105",

        "insurance_provider": "Example Health",
        "insurance_member_id": "ABC123456",

        "preferred_language": "English",

        "emergency_contact_name": "John Doe",
        "emergency_contact_phone": "415-555-5678",
    }


# ============================================================
# HELPER
# ============================================================

def create_patient():
    """
    Creates a patient and returns the API response.
    """

    response = client.post(
        "/patients",
        json=valid_patient()
    )

    return response


# ============================================================
# CREATE PATIENT TESTS
# ============================================================

def test_create_patient():
    """
    Requirement:
    POST /patients

    A valid patient should be created successfully.
    """

    response = create_patient()

    assert response.status_code == 201

    body = response.json()

    assert body["error"] is None
    assert body["data"] is not None

    assert body["data"]["first_name"] == "Jane"
    assert body["data"]["last_name"] == "Doe"

    assert "patient_id" in body["data"]
    assert "created_at" in body["data"]
    assert "updated_at" in body["data"]


def test_create_patient_contains_all_fields():
    """
    Verify that the API returns the expected demographic fields.
    """

    response = create_patient()

    assert response.status_code == 201

    data = response.json()["data"]

    expected_fields = [
        "patient_id",
        "first_name",
        "last_name",
        "date_of_birth",
        "sex",
        "phone_number",
        "email",
        "address_line_1",
        "address_line_2",
        "city",
        "state",
        "zip_code",
        "insurance_provider",
        "insurance_member_id",
        "preferred_language",
        "emergency_contact_name",
        "emergency_contact_phone",
        "created_at",
        "updated_at",
    ]

    for field in expected_fields:
        assert field in data


# ============================================================
# REQUIRED FIELD VALIDATION
# ============================================================

def test_missing_first_name():
    """
    first_name is required.
    """

    patient = valid_patient()

    del patient["first_name"]

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_missing_last_name():
    """
    last_name is required.
    """

    patient = valid_patient()

    del patient["last_name"]

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_missing_date_of_birth():
    """
    date_of_birth is required.
    """

    patient = valid_patient()

    del patient["date_of_birth"]

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_missing_sex():
    """
    sex is required.
    """

    patient = valid_patient()

    del patient["sex"]

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_missing_phone_number():
    """
    phone_number is required.
    """

    patient = valid_patient()

    del patient["phone_number"]

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_missing_address():
    """
    address_line_1 is required.
    """

    patient = valid_patient()

    del patient["address_line_1"]

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_missing_city():
    """
    city is required.
    """

    patient = valid_patient()

    del patient["city"]

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_missing_state():
    """
    state is required.
    """

    patient = valid_patient()

    del patient["state"]

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_missing_zip_code():
    """
    zip_code is required.
    """

    patient = valid_patient()

    del patient["zip_code"]

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


# ============================================================
# NAME VALIDATION
# ============================================================

def test_invalid_first_name():
    """
    first_name should contain valid name characters.
    """

    patient = valid_patient()

    patient["first_name"] = "12345"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_invalid_last_name():
    """
    last_name should contain valid name characters.
    """

    patient = valid_patient()

    patient["last_name"] = "12345"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_valid_hyphenated_name():
    """
    Hyphenated names should be accepted.
    """

    patient = valid_patient()

    patient["first_name"] = "Mary-Jane"
    patient["last_name"] = "Smith-Jones"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 201


def test_valid_apostrophe_name():
    """
    Apostrophes should be accepted in names.
    """

    patient = valid_patient()

    patient["first_name"] = "John"
    patient["last_name"] = "O'Connor"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 201


# ============================================================
# DATE OF BIRTH VALIDATION
# ============================================================

def test_invalid_future_dob():
    """
    Date of birth cannot be in the future.
    """

    patient = valid_patient()

    patient["date_of_birth"] = "2099-01-01"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_invalid_date_format():
    """
    Invalid date format should be rejected.
    """

    patient = valid_patient()

    patient["date_of_birth"] = "not-a-date"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_invalid_date_value():
    """
    Impossible calendar dates should be rejected.
    """

    patient = valid_patient()

    patient["date_of_birth"] = "1995-99-99"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


# ============================================================
# SEX VALIDATION
# ============================================================

def test_invalid_sex():
    """
    sex must be one of the allowed values.
    """

    patient = valid_patient()

    patient["sex"] = "UnknownValue"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_valid_other_sex():
    """
    Other should be accepted.
    """

    patient = valid_patient()

    patient["sex"] = "Other"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 201


def test_valid_decline_to_answer():
    """
    Decline to Answer should be accepted.
    """

    patient = valid_patient()

    patient["sex"] = "Decline to Answer"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 201


# ============================================================
# PHONE VALIDATION
# ============================================================

def test_invalid_phone():
    """
    Phone number must be a valid US phone number.
    """

    patient = valid_patient()

    patient["phone_number"] = "123"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_invalid_phone_letters():
    """
    Letters are not valid in a phone number.
    """

    patient = valid_patient()

    patient["phone_number"] = "abcdefghij"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_valid_phone_without_formatting():
    """
    A 10-digit US number should be accepted.
    """

    patient = valid_patient()

    patient["phone_number"] = "4155551234"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 201


# ============================================================
# EMAIL VALIDATION
# ============================================================

def test_invalid_email():
    """
    Email must have a valid format when supplied.
    """

    patient = valid_patient()

    patient["email"] = "not-an-email"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_email_is_optional():
    """
    Email is optional.
    """

    patient = valid_patient()

    patient["email"] = None

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 201


# ============================================================
# STATE VALIDATION
# ============================================================

def test_invalid_state():
    """
    State must be a two-letter US abbreviation.
    """

    patient = valid_patient()

    patient["state"] = "California"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_invalid_state_code():
    """
    Random state codes should be rejected.
    """

    patient = valid_patient()

    patient["state"] = "XX"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_valid_state():
    """
    Valid two-letter state abbreviation should be accepted.
    """

    patient = valid_patient()

    patient["state"] = "NY"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 201


# ============================================================
# ZIP CODE VALIDATION
# ============================================================

def test_invalid_zip_code():
    """
    ZIP code must be 5 digits or ZIP+4.
    """

    patient = valid_patient()

    patient["zip_code"] = "123"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 422


def test_valid_zip_plus_four():
    """
    ZIP+4 format should be accepted.
    """

    patient = valid_patient()

    patient["zip_code"] = "94105-1234"

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 201


# ============================================================
# OPTIONAL FIELDS
# ============================================================

def test_optional_fields_can_be_empty():
    """
    Optional fields should not prevent registration.
    """

    patient = valid_patient()

    patient["email"] = None
    patient["address_line_2"] = None
    patient["insurance_provider"] = None
    patient["insurance_member_id"] = None
    patient["preferred_language"] = None
    patient["emergency_contact_name"] = None
    patient["emergency_contact_phone"] = None

    response = client.post(
        "/patients",
        json=patient
    )

    assert response.status_code == 201


# ============================================================
# GET ALL PATIENTS
# ============================================================

def test_get_patients():
    """
    Requirement:
    GET /patients

    The API should return a list of patients.
    """

    create_response = create_patient()

    assert create_response.status_code == 201

    response = client.get("/patients")

    assert response.status_code == 200

    body = response.json()

    assert body["error"] is None
    assert isinstance(body["data"], list)


# ============================================================
# GET PATIENT BY ID
# ============================================================

def test_get_patient_by_id():
    """
    Requirement:
    GET /patients/:id
    """

    create_response = create_patient()

    assert create_response.status_code == 201

    patient_id = create_response.json()["data"]["patient_id"]

    response = client.get(
        f"/patients/{patient_id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["error"] is None
    assert body["data"]["patient_id"] == patient_id
    assert body["data"]["first_name"] == "Jane"


def test_get_nonexistent_patient():
    """
    Requesting a patient that does not exist
    should return 404.
    """

    fake_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"/patients/{fake_id}"
    )

    assert response.status_code == 404


# ============================================================
# FILTERING
# ============================================================

def test_filter_by_last_name():
    """
    GET /patients?last_name=Doe
    """

    create_response = create_patient()

    assert create_response.status_code == 201

    response = client.get(
        "/patients",
        params={
            "last_name": "Doe"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["error"] is None
    assert isinstance(body["data"], list)

    for patient in body["data"]:
        assert patient["last_name"].lower() == "doe"


def test_filter_by_date_of_birth():
    """
    GET /patients?date_of_birth=1995-03-15
    """

    create_response = create_patient()

    assert create_response.status_code == 201

    response = client.get(
        "/patients",
        params={
            "date_of_birth": "1995-03-15"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["error"] is None


def test_filter_by_phone_number():
    """
    GET /patients?phone_number=415-555-1234
    """

    create_response = create_patient()

    assert create_response.status_code == 201

    response = client.get(
        "/patients",
        params={
            "phone_number": "415-555-1234"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["error"] is None


# ============================================================
# UPDATE PATIENT
# ============================================================

def test_update_patient():
    """
    Requirement:
    PUT /patients/:id

    Partial update should be supported.
    """

    create_response = create_patient()

    assert create_response.status_code == 201

    patient_id = create_response.json()["data"]["patient_id"]

    response = client.put(
        f"/patients/{patient_id}",
        json={
            "first_name": "Janet",
            "city": "Oakland",
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["error"] is None
    assert body["data"]["first_name"] == "Janet"
    assert body["data"]["city"] == "Oakland"


def test_update_patient_email():
    """
    Verify that optional fields can be updated.
    """

    create_response = create_patient()

    assert create_response.status_code == 201

    patient_id = create_response.json()["data"]["patient_id"]

    response = client.put(
        f"/patients/{patient_id}",
        json={
            "email": "newemail@example.com"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["email"] == "newemail@example.com"


def test_update_nonexistent_patient():
    """
    Updating a non-existent patient should return 404.
    """

    fake_id = "00000000-0000-0000-0000-000000000000"

    response = client.put(
        f"/patients/{fake_id}",
        json={
            "city": "Boston"
        }
    )

    assert response.status_code == 404


# ============================================================
# DELETE / SOFT DELETE
# ============================================================

def test_delete_patient():
    """
    Requirement:
    DELETE /patients/:id

    The patient should be soft-deleted rather than
    physically removed from the database.
    """

    create_response = create_patient()

    assert create_response.status_code == 201

    patient_id = create_response.json()["data"]["patient_id"]

    response = client.delete(
        f"/patients/{patient_id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["error"] is None


def test_delete_nonexistent_patient():
    """
    Deleting a non-existent patient should return 404.
    """

    fake_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(
        f"/patients/{fake_id}"
    )

    assert response.status_code == 404


# ============================================================
# RESPONSE ENVELOPE
# ============================================================

def test_response_envelope():
    """
    API responses should follow:

    {
        "data": {...},
        "error": null
    }
    """

    response = create_patient()

    assert response.status_code == 201

    body = response.json()

    assert "data" in body
    assert "error" in body

    assert body["error"] is None


# ============================================================
# PATIENT ID UUID
# ============================================================

def test_patient_id_is_uuid():
    """
    patient_id should be automatically generated
    as a UUID.
    """

    import uuid

    response = create_patient()

    assert response.status_code == 201

    patient_id = response.json()["data"]["patient_id"]

    uuid_object = uuid.UUID(patient_id)

    assert str(uuid_object) == patient_id


# ============================================================
# CREATED / UPDATED TIMESTAMPS
# ============================================================

def test_timestamps_are_created():
    """
    created_at and updated_at should be automatically generated.
    """

    response = create_patient()

    assert response.status_code == 201

    data = response.json()["data"]

    assert data["created_at"] is not None
    assert data["updated_at"] is not None


# ============================================================
# PERSISTENCE TEST
# ============================================================

def test_patient_can_be_retrieved_after_creation():
    """
    Basic persistence check.

    The patient created through POST should be retrievable
    through GET.
    """

    patient = valid_patient()

    create_response = client.post(
        "/patients",
        json=patient
    )

    assert create_response.status_code == 201

    created_data = create_response.json()["data"]

    patient_id = created_data["patient_id"]

    get_response = client.get(
        f"/patients/{patient_id}"
    )

    assert get_response.status_code == 200

    retrieved_data = get_response.json()["data"]

    assert retrieved_data["patient_id"] == patient_id
    assert retrieved_data["first_name"] == patient["first_name"]
    assert retrieved_data["last_name"] == patient["last_name"]
    assert retrieved_data["phone_number"] == patient["phone_number"]