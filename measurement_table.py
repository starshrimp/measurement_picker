import streamlit as st
import numpy as np
import pandas as pd

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

    # Update session state after editing
    st.session_state.selected_measurements = updated_table["Include in model"].tolist()
    return updated_table