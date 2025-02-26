import streamlit as st
import numpy as np
import pandas as pd
from visualisations import button_models
from measurement_table import display_table_attributes
from data_connector import load_all
from patient_sidebar import render_patient_sidebar
from google_sheets import GoogleSheetsManager


def patient_page():
    
    if "data" not in st.session_state:
        data, problematic_patients , ideal_patients, unprocessed_patients, patient_ids = load_all()
    else:
        data = st.session_state.data
        patient_ids = st.session_state.patient_ids

    # Create two columns: left for navigation, right for main content
    col_nav, col_main = st.columns([1, 4])  # Adjust ratios as needed

    with col_nav:
        #render_patient_sidebar(data, patient_ids)
        render_patient_sidebar()

    # Main content area
    with col_main:
        st.title("Patient Overview")

        if "patient_id" in st.session_state:
            patient_id = st.session_state["patient_id"]
            
        else:
            patient_id = 1
            st.session_state["patient_id"] = patient_id

        patient_data = data[data["Patient_ID"] == patient_id].reset_index(drop=True)

        st.header(f"Patient {patient_id}")

        if not patient_data.empty:
            is_processed = bool(patient_data["is_processed"].iloc[0])
            status_color = "green" if is_processed else "red"
            status_text = "Patient Processed" if is_processed else "Patient Not Processed"
            st.markdown(f"<div style='background-color:{status_color}; padding:10px; border-radius:5px; text-align:center; color:white;'>{status_text}</div>", unsafe_allow_html=True)
            
        if not patient_data.empty:
            updated_table = display_table_attributes(patient_data, data, patient_id)
            
            if st.button("Models"):
                button_models(patient_data, updated_table)

        
                

