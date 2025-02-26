import streamlit as st
import numpy as np
import pandas as pd
from hill_equation import plot_hill_fit, train_hill_model
from data_connector import load_all

st.set_page_config(
    page_title="All Patients",
    page_icon="📈",
    layout="wide",
)
st.title("All Patients with Hill Plots")

# Load all data (including problematic and ideal flags)
data, problematic_patients, ideal_patients, unprocessed_patients, patient_ids = load_all()

# Organize plots in rows of 3 columns
col_counter = 0
columns = st.columns(5)

# Loop over every patient in the dataset
for patient_id, patient_data in data.groupby("Patient_ID"):
    # Collect selected measurements (x and y)
    x_selected = np.array(patient_data[patient_data["selected_measurement"] == 1]["Insp. O2 (%)"])
    y_selected = np.array(patient_data[patient_data["selected_measurement"] == 1]["SpO2 (%)"])

    # Collect deselected measurements for display
    deselected_data = patient_data[patient_data["selected_measurement"] == 0]
    deselected_data_index = np.array(deselected_data.index)

    #Add a new column for per-patient numbering in original order
    patient_data = patient_data.reset_index(drop=True)
    patient_data["Measurement Nr"] = np.arange(1, len(patient_data) + 1)

    # Extract measurement numbers for selected and deselected data
    measurement_numbers_selected = patient_data.loc[patient_data["selected_measurement"] == 1, "Measurement Nr"].values
    deselected_data_index = patient_data.loc[patient_data["selected_measurement"] == 0, "Measurement Nr"].values


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
                if patient_data["is_problematic"].any():
                    st.write(f":red-background[Patient ID: {patient_id} - MSE: {mse:.4f}]")
                elif patient_data["is_ideal"].any():
                    st.write(f":green-background[Patient ID: {patient_id} - MSE: {mse:.4f}]")
                else:
                    st.write(f"[Patient ID: {patient_id} - MSE: {mse:.4f}]")
                
                st.pyplot(fig)
                st.markdown("</div>", unsafe_allow_html=True)

            # Update column counter for a 3-column layout
            col_counter += 1
            if col_counter == 5:
                col_counter = 0
                columns = st.columns(5)

        except Exception as e:
            st.error(f"Error fitting Hill for Patient ID {patient_id}: {e}")
    else:
        st.warning(f"Patient ID {patient_id} has no selected measurements to process.")
