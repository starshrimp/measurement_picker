import streamlit as st
import numpy as np
import pandas as pd
from sigmoid import plot_sigmoid_fit, train_sigmoid_model
from google_sheets import GoogleSheetsManager


def start_page():
    # Setup Google Sheets manager
    secrets = st.secrets["connections"]["gsheets"]
    sheet_manager = GoogleSheetsManager(secrets)
    sheet = sheet_manager.get_sheet("anonymized_219")

    # Load data from Google Sheets
    data = pd.DataFrame(sheet.get_all_records())

    st.title("Patient Overview")

    # Number input for direct navigation to patient page
    patient_id = st.number_input("Enter Patient ID", min_value=1, step=1)
    if st.button("Go to Patient Page"):
        st.session_state.patient_id = patient_id
        st.session_state.page = "patient"
        st.rerun()

    # Button to navigate to next unprocessed patient
    if st.button("Go to First Unprocessed Patient"):
        # Find the first measurement for each patient based on the lowest Insp. O2 (%)
        first_measurements = data.sort_values(["Patient_ID", "Insp. O2 (%)"]).groupby("Patient_ID").head(1)
        
        # Filter patients where the first measurement is not processed
        unprocessed_patients = first_measurements[first_measurements["is_processed"] != 1]
        
        # Sort by Patient_ID to ensure consecutive order
        unprocessed_patients = unprocessed_patients.sort_values("Patient_ID")
        
        # Check if there are any unprocessed patients
        if not unprocessed_patients.empty:
            # Set session state to the Patient_ID of the first unprocessed patient
            st.session_state.patient_id = unprocessed_patients["Patient_ID"].iloc[0]
            st.session_state.page = "patient"
            st.rerun()
        else:
            st.warning("No unprocessed patients found.")


    # Display all "is_ideal" patients with sigmoid plots

    # Identify patients where the first measurement has is_ideal = 1
    first_measurements = data.sort_values(["Patient_ID", "Insp. O2 (%)"]).groupby("Patient_ID").head(1)
    ideal_patient_ids = first_measurements[first_measurements["is_ideal"] == 1]["Patient_ID"].unique()

    # Filter all measurements for those patients
    ideal_patients = data[data["Patient_ID"].isin(ideal_patient_ids)]


    # Display all "is_ideal" patients with sigmoid plots
    st.subheader("Ideal Patients")

    if not ideal_patients.empty:
        # Counter for organizing plots in rows
        col_counter = 0
        columns = st.columns(3)  # Create three columns for each row
        for patient_id, patient_data in ideal_patients.groupby("Patient_ID"):
            # Collect all x (Insp. O2) and y (SpO2) data points for the patient
            x_selected = patient_data[patient_data["selected_measurement"] == 1]["Insp. O2 (%)"].values
            y_selected = patient_data[patient_data["selected_measurement"] == 1]["SpO2 (%)"].values

            # Collect deselected data points for visualization
            deselected_data = patient_data[patient_data["selected_measurement"] == 0]

            # Use the index of the selected measurements as labels
            measurement_numbers_selected = patient_data[patient_data["selected_measurement"] == 1].index.values

            # Train the sigmoid model
            if len(x_selected) > 0 and len(y_selected) > 0:
                try:
                    popt = train_sigmoid_model(x_selected, y_selected)

                    # Adjust deselected data to use the index as labels
                    deselected_data_index = deselected_data.index.values

                    # Plot sigmoid fit and data points
                    fig, mse = plot_sigmoid_fit(
                        x_selected,
                        y_selected,
                        popt,
                        deselected_data={
                            "Insp. O2 (%)": deselected_data["Insp. O2 (%)"].values,
                            "SpO2 (%)": deselected_data["SpO2 (%)"].values,
                            "Measurement Nr": deselected_data_index,  # Using index as labels for deselected data
                        },
                        measurement_numbers_selected=measurement_numbers_selected,
                    )

                    # Display plot in one of the three columns
                    with columns[col_counter]:
                        st.write(f"Patient ID: {patient_id} - MSE: {mse:.4f}")
                        st.pyplot(fig)

                    # Update column counter
                    col_counter += 1

                    # Reset columns if all three columns in a row are filled
                    if col_counter == 3:
                        col_counter = 0
                        columns = st.columns(3)  # Start a new row of three columns

                except Exception as e:
                    st.error(f"Error fitting sigmoid for Patient ID {patient_id}: {e}")
            else:
                st.warning(f"Patient ID {patient_id} has no selected measurements to process.")

    else:
        st.info("No ideal patients available.")



