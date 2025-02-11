import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from sigmoid import sigmoid, train_sigmoid_model, plot_sigmoid_fit  # Import sigmoid logic
from google_sheets import GoogleSheetsManager  # Import Google Sheets manager

# Streamlit Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read()

# Google Sheets setup
secrets = st.secrets["connections"]["gsheets"]
sheet_manager = GoogleSheetsManager(secrets)  # Instantiate Google Sheets Manager
sheet = sheet_manager.get_sheet("anonymized_219")

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
                    
                    # Plot the results using the imported function
                    fig, mse = plot_sigmoid_fit(x_selected, y_selected, popt, deselected_data, measurement_numbers_selected)
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
                updates = [
                    (patient_data.index[i] + 2, 5, int(selected))  # Update selected_measurement
                    for i, selected in enumerate(st.session_state.selected_measurements)
                ]
                sheet_manager.update_multiple_cells(sheet, updates)
                
                # Update "is_ideal" and "is_processed" for all rows of the current patient
                patient_rows = patient_data.index + 2
                updates = []
                for row in patient_rows:
                    updates.append((row, 7, int(ideal_curve)))  # Update is_ideal
                    updates.append((row, 8, int(is_processed)))  # Update is_processed
                
                sheet_manager.update_multiple_cells(sheet, updates)

                st.success("Patient data saved!")
            except Exception as e:
                st.error(f"Error saving patient data: {e}")

    else:
        st.warning("No data found for the given Patient ID.")
