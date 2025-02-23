import streamlit as st
import numpy as np
import pandas as pd
from hill_equation import plot_hill_fit, train_hill_model
from data_connector import load_all

st.title("All Patients with Hill Plots")

# Load all data (including problematic and ideal flags)
data, problematic_patients, ideal_patients, patient_ids = load_all()

# Organize plots in rows of 3 columns
col_counter = 0
columns = st.columns(3)

# Loop over every patient in the dataset
for patient_id, patient_data in data.groupby("Patient_ID"):

    # Determine the border color based on flags
    if patient_data["is_problematic"].any():
        border_color = "red"
    elif patient_data["is_ideal"].any():
        border_color = "green"
    else:
        border_color = "transparent"  # No visible border

    # Collect selected measurements (x and y)
    x_selected = patient_data[patient_data["selected_measurement"] == 1]["Insp. O2 (%)"].values
    y_selected = patient_data[patient_data["selected_measurement"] == 1]["SpO2 (%)"].values

    # Collect deselected measurements for display
    deselected_data = patient_data[patient_data["selected_measurement"] == 0]
    deselected_data_index = deselected_data.index.values
    measurement_numbers_selected = patient_data[patient_data["selected_measurement"] == 1].index.values

    if len(x_selected) > 0 and len(y_selected) > 0:
        try:
            # Train the model and plot
            popt = train_hill_model(x_selected, y_selected)
            fig, mse = plot_hill_fit(
                x_selected,
                y_selected,
                popt,
                deselected_data={
                    "Insp. O2 (%)": deselected_data["Insp. O2 (%)"].values,
                    "SpO2 (%)": deselected_data["SpO2 (%)"].values,
                    "Measurement Nr": deselected_data_index,
                },
                measurement_numbers_selected=measurement_numbers_selected,
            )

            # Place the figure in one of the three columns with a colored border
            with columns[col_counter]:
                st.markdown(
                    f"""
                    <div style="border:2px solid {border_color}; padding:10px;">
                    """,
                    unsafe_allow_html=True
                )
                st.write(f"Patient ID: {patient_id} - MSE: {mse:.4f}")
                st.pyplot(fig)
                st.markdown("</div>", unsafe_allow_html=True)

            # Update column counter for a 3-column layout
            col_counter += 1
            if col_counter == 3:
                col_counter = 0
                columns = st.columns(3)

        except Exception as e:
            st.error(f"Error fitting Hill for Patient ID {patient_id}: {e}")
    else:
        st.warning(f"Patient ID {patient_id} has no selected measurements to process.")
