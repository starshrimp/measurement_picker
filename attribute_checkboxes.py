import streamlit as st
import pandas as pd 
import numpy as np

def attribute_checkboxes(patient_data, patient_id):
    # Get the current patient’s attribute values
    is_ideal = bool(patient_data.loc[0, "is_ideal"])
    is_processed = bool(patient_data.loc[0, "is_processed"])
    is_problematic = bool(patient_data.loc[0, "is_problematic"])
    comment = patient_data.loc[0, "comment"]

    # If the selected patient has changed, update session state values accordingly
    if "current_patient_id" not in st.session_state or st.session_state.current_patient_id != patient_id:
        st.session_state.ideal_curve_checkbox = is_ideal
        st.session_state.is_processed_toggle = is_processed
        st.session_state.is_problematic_checkbox = is_problematic
        st.session_state.txt = comment
        st.session_state.current_patient_id = patient_id

    # Render the checkboxes using session state values
    ideal_curve = st.checkbox(
        "Does this patient have an ideal curve?",
        key="ideal_curve_checkbox",
    )
    is_problematic = st.checkbox(
        "Is this patient considered problematic?",
        key="is_problematic_checkbox",
    )
    st.text("If you are done processing this patient, activate the toggle switch below to mark them as processed, then press the Save Updates button.")
    is_processed = st.toggle(
        label="Done processing this patient?",
        key="is_processed_toggle",
    )

    txt = st.text_area(
    "Provide Additional Comments here:",
    f"{comment}",
    )

    st.session_state.txt = txt


