import streamlit as st
from start_page import start_page
from patient_page import patient_page

st.set_page_config(
    page_title="Main",
    page_icon="🔎",
)

# Initialize Streamlit session state for navigation and patient ID
if "page" not in st.session_state:
    st.session_state.page = "start"
if "patient_id" not in st.session_state:
    st.session_state.patient_id = None

# Navigation handler
if st.session_state.page == "start":
    start_page()
elif st.session_state.page == "patient":
    patient_page()
