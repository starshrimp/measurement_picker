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

    st.markdown("### Patient Filters")
    show_ideal = st.checkbox("Filter for Ideal", value=False)
    show_problematic = st.checkbox("Filter for Problematic", value=False)
    show_processed = st.checkbox("Filter for Processed", value=False)
    show_unprocessed = st.checkbox("Filter for Unprocessed", value=False)

    selected_filters = {
        "ideal": show_ideal,
        "processed": show_processed,
        "problematic": show_problematic,
        "unprocessed": show_unprocessed,
    }
    
    # Filter patient IDs based on selection
    filtered_patient_ids = []
    for pid in patient_ids:
        if selected_filters["ideal"] and not is_ideal(data, pid):
            continue
        if selected_filters["processed"] and not is_processed(data, pid):
            continue
        if selected_filters["problematic"] and not is_problematic(data, pid):
            continue
        if selected_filters["unprocessed"] and not is_unprocessed(data, pid):
            continue
        
        filtered_patient_ids.append(pid)
    
    st.markdown("#### Patient List")
    st.markdown("<div class='scrollable-patient-list'>", unsafe_allow_html=True)
    
    for pid in sorted(filtered_patient_ids):
        label = f"Patient {pid}: {get_status_label(data, pid)}"
        if st.button(label, key=f"select_{pid}"):
            st.session_state["patient_id"] = pid
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
