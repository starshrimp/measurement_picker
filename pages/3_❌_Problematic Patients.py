import streamlit as st
import numpy as np
import pandas as pd
from hill_equation import plot_hill_fit, train_hill_model
from data_connector import load_all

st.set_page_config(
    page_title="Problematic Patients",
    page_icon="❌",
)

# Display all "is_problematic" patients with hill plots
st.subheader("Problematic Patients")
data, problematic_patients, ideal_patients, patient_ids = load_all()

if not problematic_patients.empty:
    # Counter for organizing plots in rows
    col_counter = 0
    columns = st.columns(3)  # Create three columns for each row
    for patient_id, patient_data in problematic_patients.groupby("Patient_ID"):
        # Collect all x (Insp. O2) and y (SpO2) data points for the patient
        x_selected = patient_data[patient_data["selected_measurement"] == 1]["Insp. O2 (%)"].values
        y_selected = patient_data[patient_data["selected_measurement"] == 1]["SpO2 (%)"].values

        # Collect deselected data points for visualization
        deselected_data = patient_data[patient_data["selected_measurement"] == 0]

        # Use the index of the selected measurements as labels
        measurement_numbers_selected = patient_data[patient_data["selected_measurement"] == 1].index.values

        # Train the hill model
        if len(x_selected) > 0 and len(y_selected) > 0:
            try:
                popt = train_hill_model(x_selected, y_selected)

                # Adjust deselected data to use the index as labels
                deselected_data_index = deselected_data.index.values

                # Plot hill fit and data points
                fig, mse = plot_hill_fit(
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
                st.error(f"Error fitting Hill for Patient ID {patient_id}: {e}")
        else:
            st.warning(f"Patient ID {patient_id} has no selected measurements to process.")

else:
    st.info("No problematic patients available.")


