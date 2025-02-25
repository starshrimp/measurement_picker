import streamlit as st
import numpy as np
import pandas as pd
from sigmoid import button_sigmoid_model
from hill_equation import button_hill_model
from patient_controls import render_patient_controls
from measurement_table import measurement_table
from attribute_checkboxes import attribute_checkboxes
from data_connector import load_all, save_data
from google_sheets import GoogleSheetsManager


def patient_page():
    data, problematic_patients , ideal_patients, unprocessed_patients, patient_ids = load_all()

    st.title("Patient Overview")

    render_patient_controls(data)

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
            updated_table = measurement_table(patient_data)

          
            if st.button("Sigmoid Model"):
                button_sigmoid_model(patient_data, updated_table)

          
            if st.button("Hill Model"):
                button_hill_model(patient_data, updated_table)

            st.subheader("Patient Markings")

            attribute_checkboxes(patient_data)

            if st.button("Save Patient"):
                save_data(data, patient_id)


        else:
            st.warning("No data found for the given Patient ID.")

