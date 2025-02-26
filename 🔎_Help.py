import streamlit as st
from start_page import start_page

# Initialize Streamlit session state for navigation and patient ID
if "page" not in st.session_state:
    st.session_state.page = "start"
    st.balloons()
    
if "patient_id" not in st.session_state:
    st.session_state.patient_id = 1

start_page()

