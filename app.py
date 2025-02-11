import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_gsheets import GSheetsConnection
from scipy.optimize import curve_fit
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read()

# Extract credentials from Streamlit secrets
# Extract credentials from Streamlit secrets
secrets = st.secrets["connections"]["gsheets"]


credentials_dict = {
    "type": secrets["type"],
    "project_id": secrets["project_id"],
    "private_key_id": secrets["private_key_id"],
    "private_key": secrets["private_key"].replace("\\n", "\n"),  # Ensure proper newline formatting
    "client_email": secrets["client_email"],
    "client_id": secrets["client_id"],
    "auth_uri": secrets["auth_uri"],
    "token_uri": secrets["token_uri"],
    "auth_provider_x509_cert_url": secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": secrets["client_x509_cert_url"]
}

# Setup gspread for writing back to the sheet using secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("anonymized_219").sheet1

# Sigmoid Function
def sigmoid(x, a, b, c):
    return c / (1 + np.exp(-(x - a) / b))

def train_sigmoid_model(x_data, y_data):
    popt, _ = curve_fit(sigmoid, x_data, y_data, maxfev=10000)
    return popt

# Streamlit App
st.title("Patient Measurements Viewer")

# Page 1: Input Patient ID
st.header("Select Patient")
patient_id = st.number_input("Enter Patient ID", min_value=1, step=1)

if st.button("Load Patient Data"):
    st.session_state["patient_id"] = patient_id

if "patient_id" in st.session_state:
    patient_id = st.session_state["patient_id"]
    patient_data = data[data["Patient_ID"] == patient_id].reset_index(drop=True)

    st.header(f"Patient {patient_id} Data")

    if not patient_data.empty:
        st.subheader("Measurements")

        # Add a measurement number (index-based)
        patient_data["Measurement Nr"] = patient_data.index + 1  # Start numbering from 1
        
        # Create a checkbox column for selection
        #if "selected_measurements" not in st.session_state:
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

        if st.button("Train Model"):
            # Filter selected and deselected data
            selected_data = patient_data[updated_table["Include in model"]]
            deselected_data = patient_data[~updated_table["Include in model"]]

            if not selected_data.empty:
                # Extract x (Insp. O2), y (SpO2), and Measurement Nr
                x_selected = selected_data["Insp. O2 (%)"].values
                y_selected = selected_data["SpO2 (%)"].values
                measurement_numbers_selected = selected_data["Measurement Nr"].values
                
                # Fit sigmoid model
                try:
                    popt = train_sigmoid_model(x_selected, y_selected)
                    
                    # Generate fitted curve
                    x_range = np.linspace(x_selected.min(), x_selected.max(), 100)
                    y_fitted = sigmoid(x_range, *popt)
                    
                    # Calculate MSE
                    y_pred = sigmoid(x_selected, *popt)
                    mse = np.mean((y_selected - y_pred) ** 2)

                    fig, ax = plt.subplots()

                    # Plot selected data points with measurement numbers (offset label position)
                    for i, (x, y, label) in enumerate(zip(x_selected, y_selected, measurement_numbers_selected)):
                        ax.scatter(x, y, color="blue", label="Selected Data" if i == 0 else "")
                        ax.text(x, y + 0.5, f"{label}", fontsize=10, ha="center", color="blue", fontweight="bold")

                    # Plot deselected data points with measurement numbers (offset label position)
                    for i, (x, y, label) in enumerate(zip(
                        deselected_data["Insp. O2 (%)"], deselected_data["SpO2 (%)"], deselected_data["Measurement Nr"]
                    )):
                        ax.scatter(x, y, color="grey", label="Deselected Data" if i == 0 else "", alpha=0.6)
                        ax.text(x, y + 0.5, f"{label}", fontsize=10, ha="center", color="grey", fontweight="bold")

                    ax.plot(x_range, y_fitted, color="red", label="Fitted Sigmoid")
                    ax.set_title(f"Sigmoid Fit (MSE: {mse:.4f})")
                    ax.set_xlabel("Insp. O2 (%)")
                    ax.set_ylabel("SpO2 (%)")
                    ax.legend()
                    st.pyplot(fig)

                    # Display MSE
                    st.write(f"Mean Squared Error (MSE): {mse:.4f}")

                except Exception as e:
                    st.error(f"Error in fitting sigmoid model: {e}")
            else:
                st.warning("No data points selected for fitting the model.")

        st.subheader("Patient Markings")

        ideal_curve = st.checkbox("Ideal Curve", value=bool(patient_data["is_ideal"].iloc[0]))
        is_processed = st.checkbox("Is processed?", value=bool(patient_data["is_processed"].iloc[0]))

        # Save Patient Data Button Action
        if st.button("Save Patient"):
            try:
                # Update "selected_measurement" for each row
                for i, selected in enumerate(st.session_state.selected_measurements):
                    sheet.update_cell(patient_data.index[i] + 2, 5, int(selected))  # Update selected_measurement
                
                # Update "is_ideal" and "is_processed" for all rows of the current patient
                patient_rows = patient_data.index + 2  # Adjust to match Google Sheets row indexing
                for row in patient_rows:
                    sheet.update_cell(row, 7, int(ideal_curve))  # Update is_ideal
                    sheet.update_cell(row, 8, int(is_processed))  # Update is_processed
                
                st.success("Patient data saved!")
            except Exception as e:
                st.error(f"Error saving patient data: {e}")

    else:
        st.warning("No data found for the given Patient ID.")
