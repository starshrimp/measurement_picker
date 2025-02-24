import streamlit as st
import pandas as pd
from google_sheets import GoogleSheetsManager

def load_all():
    if "data" not in st.session_state:
        st.session_state.data, st.session_state.patient_ids = load_data()
    
    # Now use st.session_state.data throughout
    data = st.session_state.data

    data["Patient_ID"] = pd.to_numeric(data["Patient_ID"], errors="coerce")
    data = data.dropna(subset=["Patient_ID"])

    patient_ids = st.session_state.patient_ids

    if "problematic_patients" not in st.session_state:
        st.session_state.problematic_patients = load_problematic_patients(data)
    
    # Now use st.session_state.data throughout
    problematic_patients = st.session_state.problematic_patients

    if "ideal_patients" not in st.session_state:
        st.session_state.ideal_patients = load_ideal_patients(data)

    ideal_patients = st.session_state.ideal_patients

    return data, problematic_patients, ideal_patients, patient_ids

def load_data():
    secrets = st.secrets["connections"]["gsheets"]
    sheet_manager = GoogleSheetsManager(secrets)
    sheet = sheet_manager.get_sheet("anonymized_219")
    data = pd.DataFrame(sheet.get_all_records())
    patient_ids = data["Patient_ID"].unique()
    return data, patient_ids

def load_problematic_patients(data):
    first_measurements = data.sort_values(["Patient_ID", "Insp. O2 (%)"]).groupby("Patient_ID").head(1)
    # Identify patients where the first measurement has is_problematic = 1
    problematic_patient_ids = first_measurements[first_measurements["is_problematic"] == 1]["Patient_ID"].unique()

    # Filter all measurements for those patients
    problematic_patients = data[data["Patient_ID"].isin(problematic_patient_ids)]
    return problematic_patients

def load_ideal_patients(data):
    # Identify patients where the first measurement has is_ideal = 1
    first_measurements = data.sort_values(["Patient_ID", "Insp. O2 (%)"]).groupby("Patient_ID").head(1)
    ideal_patient_ids = first_measurements[first_measurements["is_ideal"] == 1]["Patient_ID"].unique()

    # Filter all measurements for those patients
    ideal_patients = data[data["Patient_ID"].isin(ideal_patient_ids)]
    return ideal_patients