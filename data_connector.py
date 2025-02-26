import streamlit as st
import pandas as pd
import time
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

    if "unprocessed_patients" not in st.session_state:
        st.session_state.unprocessed_patients = load_unprocessed_patients(data)

    unprocessed_patients = st.session_state.unprocessed_patients

    return data, problematic_patients, ideal_patients, unprocessed_patients, patient_ids

def load_data():
    secrets = st.secrets["connections"]["gsheets"]
    sheet_manager = GoogleSheetsManager(secrets)
    sheet = sheet_manager.get_sheet("anonymized_219")
    data = pd.DataFrame(sheet.get_all_records())
    patient_ids = data["Patient_ID"].unique()
    
    data = add_zero_and_p50(data)
 
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

def load_unprocessed_patients(data):
    # Identify first measurements for each patient
    first_measurements = (
        data.sort_values(["Patient_ID", "Insp. O2 (%)"])
            .groupby("Patient_ID")
            .head(1)
    )
    
    # Get IDs of patients whose first measurement is unprocessed
    unprocessed_patient_ids = first_measurements[
        first_measurements["is_processed"] != 1
    ]["Patient_ID"].unique()

    # Filter and return all rows for these unprocessed patients
    unprocessed_patients = data[data["Patient_ID"].isin(unprocessed_patient_ids)]
    return unprocessed_patients


def add_zero_and_p50(data):
    # Duplicate the first row for each patient twice and modify as requested
    first_rows = data.sort_values(["Patient_ID", "Insp. O2 (%)"]).groupby("Patient_ID").head(1)
    duplicated_first_rows = first_rows.copy()
    duplicated_first_rows_1 = first_rows.copy()
    
    # Modify first duplicate
    duplicated_first_rows["Insp. O2 (%)"] = 0
    duplicated_first_rows["SpO2 (%)"] = 0
    duplicated_first_rows["selected_measurement"] = 0
    
    # Modify second duplicate
    duplicated_first_rows_1["Insp. O2 (%)"] = 9.7
    duplicated_first_rows_1["SpO2 (%)"] = 50
    duplicated_first_rows_1["selected_measurement"] = 0
    
    # Concatenate modified rows back with the original data
    data = pd.concat([duplicated_first_rows, duplicated_first_rows_1, data], ignore_index=True)
    return data


def save_data(data, patient_id):
    try:
        # Filter data for the current patient
        patient_rows = data[data["Patient_ID"] == patient_id].index + 2  # Rows in the Google Sheet (1-based index, with header)

        # Ignore the first two rows
        patient_rows = patient_rows[2:]
        st.table(patient_rows)
        
        # Ignore the first two selected measurements
        relevant_measurements = st.session_state.selected_measurements[2:]
        st.write(relevant_measurements)

        # Prepare updates for selected_measurement, is_ideal, and is_processed
        updates = []
        for i, row in enumerate(patient_rows):
            # Update "selected_measurement" for each measurement of the patient
            updates.append((row, 5, int(st.session_state.selected_measurements[i])))

        # Update "is_ideal" and "is_processed" (only for the first row of this patient in Google Sheets)
        updates.append((patient_rows[0], 7, int(st.session_state.ideal_curve_checkbox)))  # First row for is_ideal
        updates.append((patient_rows[0], 8, int(st.session_state.is_processed_toggle)))  # First row for is_processed
        updates.append((patient_rows[0], 9, int(st.session_state.is_problematic_checkbox)))  # First row for is_problematic

        secrets = st.secrets["connections"]["gsheets"]
        sheet_manager = GoogleSheetsManager(secrets)
        sheet = sheet_manager.get_sheet("anonymized_219")

        # Batch update the Google Sheet
        sheet_manager.update_multiple_cells(sheet, updates)

        st.success("Patient data saved successfully!")

    except Exception as e:
        st.error(f"Error saving patient data: {e}")

