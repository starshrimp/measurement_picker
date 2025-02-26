import streamlit as st
import numpy as np
import pandas as pd
from attribute_checkboxes import attribute_checkboxes
from patient_sidebar import render_patient_sidebar
from data_connector import save_data

def measurement_table(patient_data):
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


    return updated_table

def display_table_attributes(patient_data, data, patient_id):
    col1, col2 = st.columns([2, 2])

    with col1:
        updated_table = measurement_table(patient_data)
    with col2:
        st.markdown("<div style='padding-top: 100px;'>", unsafe_allow_html=True)
        attribute_checkboxes(patient_data, patient_id)
        if st.button("Save Updates"):
            st.session_state.selected_measurements = updated_table["Include in model"].tolist()
            
            patient_data["selected_measurement"] = st.session_state.selected_measurements
            save_data(data, patient_id)
            
        st.text("This button will save the changes from the table on the left as well as the selections from the checkboxes on top to the database.")
        st.markdown("</div>", unsafe_allow_html=True)
    return updated_table
        