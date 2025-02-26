import streamlit as st
from data_connector import load_all

if "data" not in st.session_state:
    data, problematic_patients , ideal_patients, unprocessed_patients, patient_ids = load_all()
else:
    data = st.session_state.data
    patient_ids = st.session_state.patient_ids

def is_ideal(data, pid):
    return bool(data[data["Patient_ID"] == pid]["is_ideal"].iloc[0])

def is_problematic(data, pid):
    return bool(data[data["Patient_ID"] == pid]["is_problematic"].iloc[0])

def is_unprocessed(data, pid):
    return bool(data[data["Patient_ID"] == pid]["is_processed"].iloc[0]) == False

def is_processed(data, pid):
    
    return bool(data[data["Patient_ID"] == pid]["is_processed"].iloc[0]) == True
    

def get_status_label(data, pid):
    labels = []
    if is_ideal(data, pid):
        labels.append("ideal")
    if is_processed(data, pid):
        labels.append("processed")
    else:
        labels.append("not processed")
    if is_problematic(data, pid):
        labels.append("problematic")
    return ", ".join(labels)

def render_patient_sidebar():
    if "data" not in st.session_state:
        data, problematic_patients , ideal_patients, unprocessed_patients, patient_ids = load_all()
    else:
        data = st.session_state.data
        patient_ids = st.session_state.patient_ids

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

    # Selectbox for patient selection
    selected_patient_id = st.selectbox(
        "Select Patient ID",
        options=patient_ids,
        index=list(patient_ids).index(st.session_state.get("patient_id", patient_ids[0]))
    )

    
    if selected_patient_id != st.session_state.get("patient_id"):
        st.session_state["patient_id"] = selected_patient_id
        st.rerun()  # Ensure UI updates when a different patient is selected

    # Scrollable patient list
    st.markdown("#### Patient List")
    st.markdown("<div class='scrollable-patient-list'>", unsafe_allow_html=True)

    for pid in sorted(patient_ids):
        if is_ideal(data, pid) and not show_ideal:
            continue
        if is_problematic(data, pid) and not show_problematic:
            continue
        if is_processed(data, pid) and not show_processed:
            continue
        if is_unprocessed(data, pid) and not show_unprocessed:
            continue

        label = f"Patient {pid}: {get_status_label(data, pid)}"
        if st.button(label, key=f"select_{pid}"):
            st.session_state["patient_id"] = pid
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
