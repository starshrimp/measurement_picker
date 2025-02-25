import streamlit as st
import pandas as pd 
import numpy as np

def attribute_checkboxes(patient_data):
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