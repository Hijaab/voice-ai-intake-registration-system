import os
from datetime import datetime, timezone

import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000"
).rstrip("/")


st.set_page_config(
    page_title="Voice AI Patient Dashboard",
    page_icon="🎙️",
    layout="wide",
)


# ============================================================
# API FUNCTIONS
# ============================================================

def get_patients():
    """
    Get all patients from the FastAPI backend.
    """

    try:
        response = requests.get(
            f"{API_BASE_URL}/patients",
            timeout=10,
        )

        response.raise_for_status()

        result = response.json()

        return result.get("data", [])

    except requests.exceptions.RequestException as e:

        st.error(
            f"Unable to connect to the backend API: {e}"
        )

        return []


def get_patient(patient_id):
    """
    Get a single patient by UUID.
    """

    try:
        response = requests.get(
            f"{API_BASE_URL}/patients/{patient_id}",
            timeout=10,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        result = response.json()

        return result.get("data")

    except requests.exceptions.RequestException as e:

        st.error(
            f"Unable to retrieve patient: {e}"
        )

        return None


# ============================================================
# HEADER
# ============================================================

st.title("🎙️ Voice AI Patient Registration")

st.caption(
    "Patient Intake Management Dashboard"
)

st.write(
    "View patient records registered through the Voice AI agent."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a page",
    [
        "Dashboard",
        "Patient Records",
    ],
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.header("📊 Dashboard")

    patients = get_patients()

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    total_patients = len(patients)

    today = datetime.now(timezone.utc).date()

    registered_today = 0

    for patient in patients:

        created_at = patient.get("created_at")

        if created_at:

            try:

                created_date = (
                    datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    ).date()
                )

                if created_date == today:
                    registered_today += 1

            except (ValueError, TypeError):
                pass


    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Patients",
            total_patients,
        )

    with col2:

        st.metric(
            "Registered Today",
            registered_today,
        )

    with col3:

        st.metric(
            "System Status",
            "Online",
        )


    st.divider()


    # --------------------------------------------------------
    # RECENT PATIENTS
    # --------------------------------------------------------

    st.subheader("🕐 Recent Patients")

    if not patients:

        st.info(
            "No patients have been registered yet."
        )

    else:

        # Show newest records first
        sorted_patients = sorted(
            patients,
            key=lambda p: p.get("created_at", ""),
            reverse=True,
        )

        recent_patients = sorted_patients[:5]


        for patient in recent_patients:

            first_name = patient.get(
                "first_name",
                "",
            )

            last_name = patient.get(
                "last_name",
                "",
            )

            patient_id = patient.get(
                "patient_id",
                "N/A",
            )

            with st.expander(
                f"👤 {first_name} {last_name}"
            ):

                st.write(
                    f"**Patient ID:** {patient_id}"
                )

                st.write(
                    f"**Date of Birth:** "
                    f"{patient.get('date_of_birth', 'N/A')}"
                )

                st.write(
                    f"**Sex:** "
                    f"{patient.get('sex', 'N/A')}"
                )

                st.write(
                    f"**Phone:** "
                    f"{patient.get('phone_number', 'N/A')}"
                )

                st.write(
                    f"**Email:** "
                    f"{patient.get('email', 'N/A')}"
                )

                st.write(
                    f"**City:** "
                    f"{patient.get('city', 'N/A')}"
                )

                st.write(
                    f"**State:** "
                    f"{patient.get('state', 'N/A')}"
                )


# ============================================================
# PATIENT RECORDS
# ============================================================

elif page == "Patient Records":

    st.header("📋 Patient Records")

    patients = get_patients()


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    st.subheader("🔎 Search Patients")

    search_col1, search_col2, search_col3 = st.columns(3)


    with search_col1:

        search_last_name = st.text_input(
            "Last Name"
        )


    with search_col2:

        search_phone = st.text_input(
            "Phone Number"
        )


    with search_col3:

        search_dob = st.text_input(
            "Date of Birth",
            placeholder="MM/DD/YYYY",
        )


    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    filtered_patients = patients


    if search_last_name:

        filtered_patients = [

            patient
            for patient in filtered_patients

            if search_last_name.lower()
            in patient.get(
                "last_name",
                ""
            ).lower()

        ]


    if search_phone:

        normalized_search_phone = (
            search_phone
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
            .replace("+1", "")
        )

        filtered_patients = [

            patient
            for patient in filtered_patients

            if normalized_search_phone
            in patient.get(
                "phone_number",
                ""
            ).replace(" ", "")
             .replace("-", "")
             .replace("(", "")
             .replace(")", "")
             .replace("+1", "")

        ]


    if search_dob:

        filtered_patients = [

            patient
            for patient in filtered_patients

            if search_dob
            in patient.get(
                "date_of_birth",
                ""
            )

        ]


    st.divider()


    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    st.write(
        f"Showing **{len(filtered_patients)}** patient(s)"
    )


    if not filtered_patients:

        st.info(
            "No patient records found."
        )


    else:

        for patient in filtered_patients:

            patient_id = patient.get(
                "patient_id",
                "N/A",
            )

            first_name = patient.get(
                "first_name",
                "",
            )

            last_name = patient.get(
                "last_name",
                "",
            )


            with st.expander(
                f"👤 {first_name} {last_name} "
                f"— {patient_id}"
            ):

                # ==================================================
                # PERSONAL INFORMATION
                # ==================================================

                st.subheader(
                    "Personal Information"
                )

                col1, col2 = st.columns(2)


                with col1:

                    st.write(
                        f"**First Name:** "
                        f"{patient.get('first_name', 'N/A')}"
                    )

                    st.write(
                        f"**Last Name:** "
                        f"{patient.get('last_name', 'N/A')}"
                    )

                    st.write(
                        f"**Date of Birth:** "
                        f"{patient.get('date_of_birth', 'N/A')}"
                    )

                    st.write(
                        f"**Sex:** "
                        f"{patient.get('sex', 'N/A')}"
                    )


                with col2:

                    st.write(
                        f"**Phone:** "
                        f"{patient.get('phone_number', 'N/A')}"
                    )

                    st.write(
                        f"**Email:** "
                        f"{patient.get('email', 'N/A')}"
                    )

                    st.write(
                        f"**Preferred Language:** "
                        f"{patient.get('preferred_language', 'English')}"
                    )


                st.divider()


                # ==================================================
                # ADDRESS
                # ==================================================

                st.subheader(
                    "🏠 Address"
                )


                st.write(
                    f"**Address Line 1:** "
                    f"{patient.get('address_line_1', 'N/A')}"
                )

                st.write(
                    f"**Address Line 2:** "
                    f"{patient.get('address_line_2', 'N/A')}"
                )


                address_col1, address_col2, address_col3 = st.columns(3)


                with address_col1:

                    st.write(
                        f"**City:** "
                        f"{patient.get('city', 'N/A')}"
                    )


                with address_col2:

                    st.write(
                        f"**State:** "
                        f"{patient.get('state', 'N/A')}"
                    )


                with address_col3:

                    st.write(
                        f"**ZIP Code:** "
                        f"{patient.get('zip_code', 'N/A')}"
                    )


                st.divider()


                # ==================================================
                # INSURANCE
                # ==================================================

                st.subheader(
                    "🏥 Insurance"
                )


                insurance_col1, insurance_col2 = st.columns(2)


                with insurance_col1:

                    st.write(
                        f"**Insurance Provider:** "
                        f"{patient.get('insurance_provider', 'N/A')}"
                    )


                with insurance_col2:

                    st.write(
                        f"**Member ID:** "
                        f"{patient.get('insurance_member_id', 'N/A')}"
                    )


                st.divider()


                # ==================================================
                # EMERGENCY CONTACT
                # ==================================================

                st.subheader(
                    "🚨 Emergency Contact"
                )


                emergency_col1, emergency_col2 = st.columns(2)


                with emergency_col1:

                    st.write(
                        f"**Name:** "
                        f"{patient.get('emergency_contact_name', 'N/A')}"
                    )


                with emergency_col2:

                    st.write(
                        f"**Phone:** "
                        f"{patient.get('emergency_contact_phone', 'N/A')}"
                    )


                st.divider()


                # ==================================================
                # SYSTEM INFORMATION
                # ==================================================

                st.subheader(
                    "⚙️ System Information"
                )


                st.write(
                    f"**Patient ID:** "
                    f"{patient_id}"
                )

                st.write(
                    f"**Created At:** "
                    f"{patient.get('created_at', 'N/A')}"
                )

                st.write(
                    f"**Updated At:** "
                    f"{patient.get('updated_at', 'N/A')}"
                )