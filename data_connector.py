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
    # Store original indices
    original_indices = data.index

    # Identify first measurement for each patient
    first_rows = data.sort_values(["Patient_ID", "Insp. O2 (%)"]).groupby("Patient_ID").head(1).copy()

    # Create duplicates without modifying original data indices
    duplicated_first_rows_0 = first_rows.copy()
    duplicated_first_rows_p50 = first_rows.copy()

    # Modify first duplicate for 0/0
    duplicated_first_rows_0["Insp. O2 (%)"] = 0
    duplicated_first_rows_0["SpO2 (%)"] = 0
    duplicated_first_rows_0["selected_measurement"] = 0
    duplicated_first_rows_0.index = range(len(data), len(data) + len(duplicated_first_rows_0))

    # Modify second duplicate for P50
    duplicated_first_rows_p50["Insp. O2 (%)"] = 9.7
    duplicated_first_rows_p50["SpO2 (%)"] = 50
    duplicated_first_rows_p50["selected_measurement"] = 0
    duplicated_first_rows_p50.index = range(len(data) + len(duplicated_first_rows_0), 
                                            len(data) + len(duplicated_first_rows_0) + len(duplicated_first_rows_p50))

    # Concatenate modified rows back with the original data
    data = pd.concat([data, duplicated_first_rows_0, duplicated_first_rows_p50], ignore_index=False)

    # Sort to make sure the added rows appear first for each patient
    data = data.sort_values(["Patient_ID", "Insp. O2 (%)"], ascending=[True, True])

    return data


def save_data(data, patient_id):
    try:
        # Filter data for the current patient
        patient_rows = data[data["Patient_ID"] == patient_id].index + 2  # Rows in the Google Sheet (1-based index, with header)
        patient_rows = patient_rows[2:]

        relevant_measurements = st.session_state.selected_measurements[2:]
        # Prepare updates for selected_measurement, is_ideal, and is_processed
        updates = []
        for i, row in enumerate(patient_rows):
            # Update "selected_measurement" for each measurement of the patient
            updates.append((row, 5, int(relevant_measurements[i])))

        # Update "is_ideal" and "is_processed" (only for the first row of this patient in Google Sheets)
        updates.append((patient_rows[0], 7, int(st.session_state.ideal_curve_checkbox)))  # First row for is_ideal
        updates.append((patient_rows[0], 8, int(st.session_state.is_processed_toggle)))  # First row for is_processed
        updates.append((patient_rows[0], 9, int(st.session_state.is_problematic_checkbox)))  # First row for is_problematic
        updates.append((patient_rows[0], 10, st.session_state.txt)) 

        secrets = st.secrets["connections"]["gsheets"]
        sheet_manager = GoogleSheetsManager(secrets)
        sheet = sheet_manager.get_sheet("anonymized_219")

        # Batch update the Google Sheet
        sheet_manager.update_multiple_cells(sheet, updates)

        data.loc[patient_rows, "selected_measurement"] = relevant_measurements
        data.loc[patient_rows[0], "is_ideal"] = int(st.session_state.ideal_curve_checkbox)
        data.loc[patient_rows[0], "is_processed"] = int(st.session_state.is_processed_toggle)
        data.loc[patient_rows[0], "is_problematic"] = int(st.session_state.is_problematic_checkbox)
        data.loc[patient_rows[0], "comment"] = st.session_state.txt

        # Update session state immediately after saving to Google Sheets
        st.session_state.data.loc[data["Patient_ID"] == patient_id, "is_ideal"] = int(st.session_state.ideal_curve_checkbox)
        st.session_state.data.loc[data["Patient_ID"] == patient_id, "is_processed"] = int(st.session_state.is_processed_toggle)
        st.session_state.data.loc[data["Patient_ID"] == patient_id, "is_problematic"] = int(st.session_state.is_problematic_checkbox)
        st.session_state.data.loc[data["Patient_ID"] == patient_id, "comment"] = st.session_state.txt

        st.toast("Patient data saved successfully!", icon='😍')
        st.success("Patient data saved successfully!")
        time.sleep(2)
        st.rerun()
        
        
    except Exception as e:
        st.error(f"Error saving patient data: {e}")

