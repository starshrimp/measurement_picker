import streamlit as st
import numpy as np
import pandas as pd
from sigmoid import plot_sigmoid_fit, train_sigmoid_model
from google_sheets import GoogleSheetsManager


def patient_page():
    # Setup Google Sheets manager
    secrets = st.secrets["connections"]["gsheets"]
    sheet_manager = GoogleSheetsManager(secrets)
    sheet = sheet_manager.get_sheet("anonymized_219")

    # Load data from Google Sheets
    data = pd.DataFrame(sheet.get_all_records())

    st.title("Patient Overview")

    if st.button("Back to Overview"):
        st.session_state.page = "start"
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


    if st.button("Go to Next Patient"):
        if "patient_id" in st.session_state:
            current_patient_id = st.session_state["patient_id"]
            next_patients = data[data["Patient_ID"] > current_patient_id].sort_values("Patient_ID")
            if not next_patients.empty:
                st.session_state.patient_id = next_patients["Patient_ID"].iloc[0]
                st.session_state.page = "patient"
                st.rerun()
            else:
                st.warning("No more patients available with a higher Patient ID.")
        else:
            st.warning("No current patient selected. Please start from an unprocessed patient.")


    if "patient_id" in st.session_state:
        patient_id = st.session_state["patient_id"]
        patient_data = data[data["Patient_ID"] == patient_id].reset_index(drop=True)

        st.header(f"Patient {patient_id}")

        if not patient_data.empty:
            is_processed = bool(patient_data["is_processed"].iloc[0])
            status_color = "green" if is_processed else "red"
            status_text = "Patient Processed" if is_processed else "Patient Not Processed"
            st.markdown(f"<div style='background-color:{status_color}; padding:10px; border-radius:5px; text-align:center; color:white;'>{status_text}</div>", unsafe_allow_html=True)


        if not patient_data.empty:
            st.subheader("Measurements")

            # Add a measurement number (index-based)
            patient_data["Measurement Nr"] = patient_data.index + 1

            # Create a checkbox column for selection
            st.session_state.selected_measurements = patient_data["selected_measurement"].astype(bool).tolist()

            # Display table with checkboxes using st.data_editor()
            table_data = patient_data[["Measurement Nr", "Insp. O2 (%)", "SpO2 (%)"]].copy()
            table_data["Include in model"] = st.session_state.selected_measurements

            updated_table = st.data_editor(
                table_data,
                column_config={"Include in model": st.column_config.CheckboxColumn()},
                disabled=["Measurement Nr", "Insp. O2 (%)", "SpO2 (%)"],
                hide_index=True
            )

            # Update session state after editing
            st.session_state.selected_measurements = updated_table["Include in model"].tolist()

          
            if st.button("Train Model"):
                # Filter selected and deselected data
                selected_data = patient_data[updated_table["Include in model"]]
                deselected_data = patient_data[~updated_table["Include in model"]]

                if not selected_data.empty:
                    x_selected = selected_data["Insp. O2 (%)"].values
                    y_selected = selected_data["SpO2 (%)"].values
                    measurement_numbers_selected = selected_data["Measurement Nr"].values

                    try:
                        popt = train_sigmoid_model(x_selected, y_selected)
                        fig, mse = plot_sigmoid_fit(x_selected, y_selected, popt, deselected_data, measurement_numbers_selected)
                        st.pyplot(fig)
                        st.write(f"Mean Squared Error (MSE): {mse:.4f}")
                    except Exception as e:
                        st.error(f"Error in fitting sigmoid model: {e}")
                else:
                    st.warning("No data points selected for fitting the model.")

          
            st.subheader("Patient Markings")

            is_ideal = bool(patient_data.loc[0, "is_ideal"])
            is_processed = bool(patient_data.loc[0, "is_processed"])
            is_problematic = bool(patient_data.loc[0, "is_problematic"])

            # Initialize session state only if it doesn't exist
            if "ideal_curve_checkbox" not in st.session_state:
                st.session_state.ideal_curve_checkbox = is_ideal
            if "is_processed_checkbox" not in st.session_state:
                st.session_state.is_processed_checkbox = is_processed
            if "is_problematic_checkbox" not in st.session_state:
                st.session_state.is_problematic_checkbox = is_problematic

            # Use the session state for the checkbox values
            ideal_curve = st.checkbox(
                "Ideal Curve",
                key="ideal_curve_checkbox",
            )
            is_processed = st.checkbox(
                "Is processed?",
                key="is_processed_checkbox",
            )
            is_problematic = st.checkbox(
                "Is problematic?",
                key="is_problematic_checkbox",
            )
            


            if st.button("Save Patient"):
                try:
                    # Filter data for the current patient
                    patient_rows = data[data["Patient_ID"] == patient_id].index + 2  # Rows in the Google Sheet (1-based index, with header)

                    # Prepare updates for selected_measurement, is_ideal, and is_processed
                    updates = []
                    for i, row in enumerate(patient_rows):
                        # Update "selected_measurement" for each measurement of the patient
                        updates.append((row, 5, int(st.session_state.selected_measurements[i])))

                    # Update "is_ideal" and "is_processed" (only for the first row of this patient in Google Sheets)
                    updates.append((patient_rows[0], 7, int(st.session_state.ideal_curve_checkbox)))  # First row for is_ideal
                    updates.append((patient_rows[0], 8, int(st.session_state.is_processed_checkbox)))  # First row for is_processed
                    updates.append((patient_rows[0], 9, int(st.session_state.is_problematic_checkbox)))  # First row for is_problematic


                    # Batch update the Google Sheet
                    sheet_manager.update_multiple_cells(sheet, updates)

                    st.success("Patient data saved successfully!")

                except Exception as e:
                    st.error(f"Error saving patient data: {e}")


        else:
            st.warning("No data found for the given Patient ID.")
