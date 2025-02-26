import streamlit as st
import numpy as np
import pandas as pd
from sigmoid import plot_sigmoid_fit, train_sigmoid_model
from data_connector import load_all, load_data, load_problematic_patients
from google_sheets import GoogleSheetsManager

st.set_page_config(
    page_title="ODC Curve",
    page_icon="👋",
    layout="wide",
)

st.title("Oxygen Dissociation Curve (ODC) Fitting")

def start_page():

    data, problematic_patients , ideal_patients, unprocessed_patients, patient_ids = load_all()
    
    st.header("Search Patients")

    # Number input for direct navigation to patient page
    patient_id = st.selectbox("Select Patient ID", options=patient_ids)

    if st.button("Go to Patient Page"):
        st.session_state.patient_id = patient_id
        st.session_state.page = "patient"
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

    st.header("Help")
    st.markdown(
        """
        This app allows you to visualize and fit Oxygen Dissociation Curves (ODCs) for different patients. 
        You can navigate between patients, view their measurements, and fit sigmoidal curves as well as hill equations to the data.
        - <a href="Label" target="_self">Label</a>: In this section, you can label the data.
        - <a href="All_Patients" target="_self">All Patients</a>: View all patients of the train set with their respective ODC plots fitted with the Hill Equation. 
        - <a href="Ideal_Patients" target="_self">Ideal Patients</a>: View all patients of the train set that are marked with "is ideal" in the Label section, with their respective ODC plots fitted with the Hill Equation.
        - <a href="Problematic_Patients" target="_self">Problematic Patients</a>: View all patients of the train set that are marked with "is problematic" in the Label section, with their respective ODC plots fitted with the Hill Equation.
        """, unsafe_allow_html=True
    )
