import streamlit as st
import numpy as np
import pandas as pd
from data_connector import load_all


st.set_page_config(
    page_title="ODC Curve",
    page_icon="👋",
    layout="wide",
)



def start_page():

    data, problematic_patients , ideal_patients, unprocessed_patients, patient_ids = load_all()
    st.title("Oxygen Dissociation Curve (ODC) Fitting")
    
    st.header("Help")
    st.markdown(
        """
        This app allows you to visualize and fit Oxygen Dissociation Curves (ODCs) for different patients. 
        You can navigate between patients, view their measurements, and fit sigmoidal curves as well as hill equations to the data.
        - <a href="Label" target="_self">Label</a>: In this section, you can label the data.
            - There is a sidebar that lets you filter patients after attributes and whether they are processed or not.
            - The list of patients is displayed in order in the sidebar, including their labelling status.
            - In the Measurement Overview, measurements can be added and removed from the selection individually.
                - The first two "measurements" are always 0/0 as a starting point and 9.7/50, which is the P50 calculated from 19mmHg. They are visualized as general measurements by the "📚" sign behind them. They are not taken into calculation by default but can be manually added to see how it changes the plot for both the sigmoid and the hill model. They are also not saved to the database, even when selected, as they are the same for all patients.
            - Attributes can be adjusted on the right side of the page.
                - Upon finishing the processing of this patient, the toggle can be switched to "Processed" to mark the patient as processed.
                - The button "Save Updates" saves the changes made to the patient data to the Google Sheet. A success message will be displayed, and the page will reload after 2 seconds to refresh the patient list in the sidebar on the left to the updated attributes.
        - <a href="All_Patients" target="_self">All Patients</a>: View all patients of the train set with their respective ODC plots fitted with the Hill Equation. 
        - <a href="Ideal_Patients" target="_self">Ideal Patients</a>: View all patients of the train set that are marked with "is ideal" in the Label section, with their respective ODC plots fitted with the Hill Equation.
        - <a href="Problematic_Patients" target="_self">Problematic Patients</a>: View all patients of the train set that are marked with "is problematic" in the Label section, with their respective ODC plots fitted with the Hill Equation.
        """, unsafe_allow_html=True
    )
