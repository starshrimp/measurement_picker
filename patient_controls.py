import streamlit as st
import pandas as pd

def render_patient_controls(data):
    """
    Renders four navigation buttons in a row:
    Previous Patient, Previous Unprocessed Patient, Next Unprocessed Patient, Next Patient.
    Assumes 'patient_id' is managed in st.session_state.
    """

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Patient"):
            if "patient_id" in st.session_state:
                current_patient_id = int(st.session_state["patient_id"])
                data["Patient_ID"] = pd.to_numeric(data["Patient_ID"], errors="coerce")
                data.dropna(subset=["Patient_ID"], inplace=True)
                data["Patient_ID"] = data["Patient_ID"].astype(int)

                prev_patients = data[data["Patient_ID"] < current_patient_id].sort_values("Patient_ID", ascending=False)
                if not prev_patients.empty:
                    st.session_state["patient_id"] = prev_patients["Patient_ID"].iloc[0]
                    st.session_state["page"] = "patient"
                    st.rerun()
                else:
                    st.warning("No patients found with a lower Patient ID.")
            else:
                st.warning("No current patient selected.")

        if st.button("⬅️ Unprocessed"):
            if "patient_id" in st.session_state:
                current_patient_id = int(st.session_state["patient_id"])
                # Find the first measurement for each patient
                first_measurements = data.sort_values(["Patient_ID", "Insp. O2 (%)"]).groupby("Patient_ID").head(1)
                # Filter only unprocessed
                unprocessed_firsts = first_measurements[first_measurements["is_processed"] != 1].sort_values("Patient_ID")
                # Look for unprocessed patients with ID less than current
                prev_unproc = unprocessed_firsts[unprocessed_firsts["Patient_ID"] < current_patient_id].sort_values("Patient_ID", ascending=False)
                if not prev_unproc.empty:
                    st.session_state["patient_id"] = int(prev_unproc["Patient_ID"].iloc[0])
                    st.session_state["page"] = "patient"
                    st.rerun()
                else:
                    st.warning("No unprocessed patients found with a lower ID.")
            else:
                st.warning("No current patient selected.")

    with col2:
        if st.button("➡️ Patient"):
            if "patient_id" in st.session_state:
                current_patient_id = int(st.session_state["patient_id"])
                data["Patient_ID"] = pd.to_numeric(data["Patient_ID"], errors="coerce")
                data.dropna(subset=["Patient_ID"], inplace=True)
                data["Patient_ID"] = data["Patient_ID"].astype(int)

                next_patients = data[data["Patient_ID"] > current_patient_id].sort_values("Patient_ID")
                if not next_patients.empty:
                    st.session_state["patient_id"] = next_patients["Patient_ID"].iloc[0]
                    st.session_state["page"] = "patient"
                    st.rerun()
                else:
                    st.warning("No more patients with a higher Patient ID.")
            else:
                st.warning("No current patient selected.")
        if st.button("➡️ Unprocessed"):
            if "patient_id" in st.session_state:
                current_patient_id = int(st.session_state["patient_id"])
                # Find the first measurement for each patient
                first_measurements = data.sort_values(["Patient_ID", "Insp. O2 (%)"]).groupby("Patient_ID").head(1)
                # Filter only unprocessed
                unprocessed_firsts = first_measurements[first_measurements["is_processed"] != 1].sort_values("Patient_ID")
                # Look for unprocessed patients with ID greater than current
                next_unproc = unprocessed_firsts[unprocessed_firsts["Patient_ID"] > current_patient_id].sort_values("Patient_ID")
                if not next_unproc.empty:
                    st.session_state["patient_id"] = int(next_unproc["Patient_ID"].iloc[0])
                    st.session_state["page"] = "patient"
                    st.rerun()
                else:
                    st.warning("No unprocessed patients found with a higher ID.")
            else:
                st.warning("No current patient selected.")

