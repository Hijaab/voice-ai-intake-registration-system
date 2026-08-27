import streamlit as st
from datetime import datetime

from database import create_db_and_tables, get_session
from models import Patient


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Voice AI Intake Registration System",
    page_icon="🎙️",
    layout="wide",
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

create_db_and_tables()


# ============================================================
# APPLICATION TITLE
# ============================================================

st.title("🎙️ Voice AI Intake Registration System")

st.write(
    "Patient registration and intake management system."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a page",
    [
        "Patient Registration",
        "Patient Records",
    ],
)


# ============================================================
# PATIENT REGISTRATION
# ============================================================

if page == "Patient Registration":

    st.header("📝 Patient Registration")

    with st.form("patient_registration_form"):

        st.subheader("Personal Information")

        col1, col2 = st.columns(2)

        with col1:

            first_name = st.text_input(
                "First Name *"
            )

            last_name = st.text_input(
                "Last Name *"
            )

            date_of_birth = st.date_input(
                "Date of Birth"
            )

            gender = st.selectbox(
                "Gender",
                [
                    "Prefer not to say",
                    "Male",
                    "Female",
                    "Other",
                ],
            )

        with col2:

            phone = st.text_input(
                "Phone Number"
            )

            email = st.text_input(
                "Email Address"
            )

            address = st.text_area(
                "Address"
            )

            city = st.text_input(
                "City"
            )

            postal_code = st.text_input(
                "Postal Code"
            )

            country = st.text_input(
                "Country"
            )

        st.divider()

        st.subheader("Medical Information")

        symptoms = st.text_area(
            "Symptoms"
        )

        medical_history = st.text_area(
            "Medical History"
        )

        current_medications = st.text_area(
            "Current Medications"
        )

        allergies = st.text_area(
            "Allergies"
        )

        st.divider()

        st.subheader("Emergency Contact")

        emergency_contact = st.text_input(
            "Emergency Contact Name"
        )

        emergency_phone = st.text_input(
            "Emergency Contact Phone"
        )

        st.divider()

        st.subheader("Voice / AI Information")

        transcript = st.text_area(
            "Voice Transcript"
        )

        ai_summary = st.text_area(
            "AI Summary"
        )

        ai_recommendation = st.text_area(
            "AI Recommendation"
        )

        submitted = st.form_submit_button(
            "💾 Register Patient"
        )


    # ========================================================
    # SAVE PATIENT
    # ========================================================

    if submitted:

        if not first_name.strip():
            st.error("Please enter the patient's first name.")

        elif not last_name.strip():
            st.error("Please enter the patient's last name.")

        else:

            try:

                patient = Patient(
                    first_name=first_name.strip(),
                    last_name=last_name.strip(),

                    date_of_birth=str(date_of_birth),

                    gender=gender,

                    phone=phone.strip(),
                    email=email.strip(),

                    address=address.strip(),
                    city=city.strip(),
                    postal_code=postal_code.strip(),
                    country=country.strip(),

                    symptoms=symptoms.strip(),
                    medical_history=medical_history.strip(),
                    current_medications=current_medications.strip(),
                    allergies=allergies.strip(),

                    emergency_contact=emergency_contact.strip(),
                    emergency_phone=emergency_phone.strip(),

                    transcript=transcript.strip(),
                    ai_summary=ai_summary.strip(),
                    ai_recommendation=ai_recommendation.strip(),

                    created_at=datetime.now().isoformat(),
                )


                # ------------------------------------------------
                # DATABASE SESSION
                # ------------------------------------------------

                with get_session() as session:

                    session.add(patient)

                    session.commit()

                    session.refresh(patient)


                st.success(
                    f"Patient registered successfully! "
                    f"Patient ID: {patient.id}"
                )


            except Exception as e:

                st.error(
                    "An error occurred while saving the patient."
                )

                st.exception(e)


# ============================================================
# PATIENT RECORDS
# ============================================================

elif page == "Patient Records":

    st.header("📋 Patient Records")

    try:

        with get_session() as session:

            patients = session.query(Patient).all()


        if not patients:

            st.info(
                "No patient records have been registered yet."
            )

        else:

            st.write(
                f"Total patients: **{len(patients)}**"
            )

            st.divider()


            for patient in patients:

                with st.expander(
                    f"Patient #{patient.id} — "
                    f"{patient.first_name} {patient.last_name}"
                ):

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            f"**First Name:** "
                            f"{patient.first_name}"
                        )

                        st.write(
                            f"**Last Name:** "
                            f"{patient.last_name}"
                        )

                        st.write(
                            f"**Date of Birth:** "
                            f"{patient.date_of_birth or 'N/A'}"
                        )

                        st.write(
                            f"**Gender:** "
                            f"{patient.gender or 'N/A'}"
                        )

                        st.write(
                            f"**Phone:** "
                            f"{patient.phone or 'N/A'}"
                        )

                        st.write(
                            f"**Email:** "
                            f"{patient.email or 'N/A'}"
                        )

                    with col2:

                        st.write(
                            f"**City:** "
                            f"{patient.city or 'N/A'}"
                        )

                        st.write(
                            f"**Country:** "
                            f"{patient.country or 'N/A'}"
                        )

                        st.write(
                            f"**Emergency Contact:** "
                            f"{patient.emergency_contact or 'N/A'}"
                        )

                        st.write(
                            f"**Emergency Phone:** "
                            f"{patient.emergency_phone or 'N/A'}"
                        )

                    st.divider()

                    st.subheader("Symptoms")

                    st.write(
                        patient.symptoms or "N/A"
                    )

                    st.subheader("Medical History")

                    st.write(
                        patient.medical_history or "N/A"
                    )

                    st.subheader("Current Medications")

                    st.write(
                        patient.current_medications or "N/A"
                    )

                    st.subheader("Allergies")

                    st.write(
                        patient.allergies or "N/A"
                    )

                    st.subheader("Voice Transcript")

                    st.write(
                        patient.transcript or "N/A"
                    )

                    st.subheader("AI Summary")

                    st.write(
                        patient.ai_summary or "N/A"
                    )

                    st.subheader("AI Recommendation")

                    st.write(
                        patient.ai_recommendation or "N/A"
                    )

                    st.caption(
                        f"Registered: "
                        f"{patient.created_at or 'N/A'}"
                    )


    except Exception as e:

        st.error(
            "Unable to load patient records."
        )

        st.exception(e)