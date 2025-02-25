import streamlit as st
import numpy as np
import pandas as pd
from visualisations import button_models
from patient_controls import render_patient_controls
from measurement_table import display_table_attributes
from data_connector import load_all, save_data
from google_sheets import GoogleSheetsManager


def patient_page():
    data, problematic_patients , ideal_patients, unprocessed_patients, patient_ids = load_all()

    st.set_page_config(layout="wide")

    def is_ideal(pid):
        return pid in ideal_patients["Patient_ID"].values

    def is_problematic(pid):
        return pid in problematic_patients["Patient_ID"].values

    def is_unprocessed(pid):
        return pid in unprocessed_patients["Patient_ID"].values

    def is_processed(pid):
        # Here, "processed" simply means "not unprocessed", 
        # but if your data has a different logic, adjust as needed
        return not is_unprocessed(pid)
        

    def get_status_label(pid):
        labels = []
        if is_ideal(pid):
            labels.append("ideal")
        if is_processed(pid):
            labels.append("processed")
        else:
            labels.append("not processed")
        if is_problematic(pid):
            labels.append("problematic")
        return ", ".join(labels)

    # Create two columns: left for navigation, right for main content
    col_nav, col_main = st.columns([1.5, 4])  # Adjust ratios as needed

    with col_nav:
        st.markdown(
            """
            <style>
            .scrollable-patient-list {
                padding-right: 0.5rem;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown("### Patient Filters")
        show_ideal = st.checkbox("Show Ideal", value=True)
        show_processed = st.checkbox("Show Processed", value=True)
        show_problematic = st.checkbox("Show Problematic", value=True)
        show_unprocessed = st.checkbox("Show Unprocessed", value=True)

        # render_patient_controls(data)

        # Add some CSS to make the patient list scrollable
        st.markdown(
            """
            <style>
            .scrollable-patient-list {
                max-height: 400px; /* adjust as needed */
                overflow-y: auto;
                /*border: 1px solid #ccc;*/
                padding: 0.5rem;
                border-radius: 5px;
                margin-top: 0.5rem;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown("#### Patient List")
        st.markdown("<div class='scrollable-patient-list'>", unsafe_allow_html=True)

        for pid in sorted(patient_ids):
            # Filter logic based on sets
            if is_ideal(pid) and not show_ideal:
                continue
            if is_problematic(pid) and not show_problematic:
                continue
            if is_processed(pid) and not show_processed:
                continue
            if is_unprocessed(pid) and not show_unprocessed:
                continue

            label = f"Patient {pid}: {get_status_label(pid)}"
            if st.button(label, key=f"select_{pid}"):
                st.session_state["patient_id"] = pid

        st.markdown("</div>", unsafe_allow_html=True)

    # Main content area
    with col_main:


        st.title("Patient Overview")

        
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
                updated_table = display_table_attributes(patient_data, data, patient_id)

                if st.button("Models"):
                    button_models(patient_data, updated_table)

                # if st.button("Sigmoid Model"):
                #     button_sigmoid_model(patient_data, updated_table)

            
                # if st.button("Hill Model"):
                #     button_hill_model(patient_data, updated_table)

                


            else:
                st.warning("No data found for the given Patient ID.")

