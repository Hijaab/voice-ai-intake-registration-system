import os
from datetime import datetime, timezone

import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="Voice AI Patient Registration",
    page_icon="🎙️",
    layout="wide",
)


# ============================================================
# CONFIGURATION
# ============================================================

def get_api_url():

    try:
        return st.secrets["API_URL"].rstrip("/")
    except Exception:
        return os.getenv(
            "API_URL",
            "http://localhost:8001"
        ).rstrip("/")


API_URL = get_api_url()


# ============================================================
# API FUNCTIONS
# ============================================================

def get_patients():

    response = requests.get(
        f"{API_URL}/patients",
        timeout=10
    )

    response.raise_for_status()

    result = response.json()

    if result.get("error"):
        raise Exception(
            result["error"]
        )

    return result.get(
        "data",
        []
    )


def delete_patient(patient_id):

    response = requests.delete(
        f"{API_URL}/patients/{patient_id}",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# HEADER
# ============================================================

st.title(
    "🎙️ Voice AI Patient Registration"
)

st.write(
    "Patient Intake Management Dashboard"
)

st.caption(
    "View patient records registered through "
    "the Voice AI agent."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "Navigation"
)

page = st.sidebar.radio(
    "Select a page",
    [
        "Dashboard",
        "Patient Records",
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.header(
        "📊 Dashboard"
    )

    try:

        patients = get_patients()

        total_patients = len(
            patients
        )

        today = datetime.now(
            timezone.utc
        ).date()

        registered_today = 0

        for patient in patients:

            created_at = patient.get(
                "created_at"
            )

            if created_at:

                try:

                    created = datetime.fromisoformat(
                        created_at.replace(
                            "Z",
                            "+00:00"
                        )
                    )

                    if created.date() == today:
                        registered_today += 1

                except Exception:
                    pass


        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Patients",
                total_patients
            )

        with col2:

            st.metric(
                "Registered Today",
                registered_today
            )

        with col3:

            st.metric(
                "System Status",
                "Online"
            )


        st.divider()

        st.subheader(
            "🕐 Recent Patients"
        )

        if not patients:

            st.info(
                "No patients have been registered yet."
            )

        else:

            recent = patients[:10]

            table_data = []

            for patient in recent:

                table_data.append({
                    "Patient ID": str(
                        patient.get(
                            "patient_id",
                            ""
                        )
                    ),

                    "First Name": patient.get(
                        "first_name",
                        ""
                    ),

                    "Last Name": patient.get(
                        "last_name",
                        ""
                    ),

                    "DOB": patient.get(
                        "date_of_birth",
                        ""
                    ),

                    "Sex": patient.get(
                        "sex",
                        ""
                    ),

                    "Phone": patient.get(
                        "phone_number",
                        ""
                    ),

                    "City": patient.get(
                        "city",
                        ""
                    ),

                    "State": patient.get(
                        "state",
                        ""
                    ),
                })


            df = pd.DataFrame(
                table_data
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )


    except Exception as exc:

        st.error(
            "Unable to connect to the backend API."
        )

        st.code(
            str(exc)
        )

        st.info(
            f"Current API URL: {API_URL}"
        )


# ============================================================
# PATIENT RECORDS
# ============================================================

elif page == "Patient Records":

    st.header(
        "📋 Patient Records"
    )

    try:

        patients = get_patients()

        if not patients:

            st.info(
                "No patient records available."
            )

        else:

            st.write(
                f"Total patients: **{len(patients)}**"
            )

            search = st.text_input(
                "Search by first or last name"
            )


            filtered = patients

            if search.strip():

                query = search.strip().lower()

                filtered = [
                    p for p in patients
                    if query in p.get(
                        "first_name",
                        ""
                    ).lower()
                    or query in p.get(
                        "last_name",
                        ""
                    ).lower()
                ]


            for patient in filtered:

                patient_id = patient.get(
                    "patient_id"
                )

                first_name = patient.get(
                    "first_name",
                    ""
                )

                last_name = patient.get(
                    "last_name",
                    ""
                )

                with st.expander(
                    f"{first_name} {last_name} "
                    f"— {patient_id}"
                ):

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            f"**Patient ID:** "
                            f"{patient_id}"
                        )

                        st.write(
                            f"**First Name:** "
                            f"{first_name}"
                        )

                        st.write(
                            f"**Last Name:** "
                            f"{last_name}"
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

                    with col2:

                        st.write(
                            f"**Address:** "
                            f"{patient.get('address_line_1', 'N/A')}"
                        )

                        st.write(
                            f"**Address 2:** "
                            f"{patient.get('address_line_2', 'N/A')}"
                        )

                        st.write(
                            f"**City:** "
                            f"{patient.get('city', 'N/A')}"
                        )

                        st.write(
                            f"**State:** "
                            f"{patient.get('state', 'N/A')}"
                        )

                        st.write(
                            f"**ZIP:** "
                            f"{patient.get('zip_code', 'N/A')}"
                        )

                    st.divider()

                    st.subheader(
                        "Insurance"
                    )

                    st.write(
                        f"**Provider:** "
                        f"{patient.get('insurance_provider', 'N/A')}"
                    )

                    st.write(
                        f"**Member ID:** "
                        f"{patient.get('insurance_member_id', 'N/A')}"
                    )

                    st.subheader(
                        "Emergency Contact"
                    )

                    st.write(
                        f"**Name:** "
                        f"{patient.get('emergency_contact_name', 'N/A')}"
                    )

                    st.write(
                        f"**Phone:** "
                        f"{patient.get('emergency_contact_phone', 'N/A')}"
                    )

                    st.write(
                        f"**Preferred Language:** "
                        f"{patient.get('preferred_language', 'English')}"
                    )

                    st.divider()

                    if st.button(
                        "🗑️ Delete Patient",
                        key=f"delete_{patient_id}"
                    ):

                        try:

                            delete_patient(
                                patient_id
                            )

                            st.success(
                                "Patient soft-deleted."
                            )

                            st.rerun()

                        except Exception as exc:

                            st.error(
                                f"Delete failed: {exc}"
                            )

    except Exception as exc:

        st.error(
            "Unable to load patient records."
        )

        st.code(
            str(exc)
        )

        st.info(
            f"Current API URL: {API_URL}"
        )