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
        unprocessed_patients = data[data["is_processed"] == 0].sort_values("Patient_ID")
        if not unprocessed_patients.empty:
            st.session_state.patient_id = unprocessed_patients["Patient_ID"].iloc[0]
            st.session_state.page = "patient"
            st.rerun()
        else:
            st.warning("No unprocessed patients found.")

    # Display all "is_ideal" patients with sigmoid plots
    st.subheader("Ideal Patients (is_ideal = 1)")
    ideal_patients = data[data["is_ideal"] == 1]

    if not ideal_patients.empty:
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
                            "Measurement Nr": deselected_data_index  # Using index as labels for deselected data
                        }, 
                        measurement_numbers_selected=measurement_numbers_selected
                    )

                    # Display plot in Streamlit
                    st.write(f"Patient ID: {patient_id} - MSE: {mse:.4f}")
                    st.pyplot(fig)

                except Exception as e:
                    st.error(f"Error fitting sigmoid for Patient ID {patient_id}: {e}")
            else:
                st.warning(f"Patient ID {patient_id} has no selected measurements to process.")

    else:
        st.info("No ideal patients available.")


