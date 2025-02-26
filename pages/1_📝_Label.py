import streamlit as st
from patient_page import patient_page

st.set_page_config(layout="wide")

# if "authenticated" not in st.session_state:
#     st.session_state["authenticated"] = False

# # Login section if not authenticated
# if not st.session_state["authenticated"]:
#     password = st.text_input("Enter password", type="password")
#     if password:
#         if password == "master_thesis_UKBB":
#             st.session_state["authenticated"] = True
#             patient_page()
#         else:
#             st.error("Invalid password")
patient_page()