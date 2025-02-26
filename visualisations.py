import pandas as pd
import streamlit as st
from sigmoid import train_sigmoid_model, plot_sigmoid_fit
from hill_equation import train_hill_model, plot_hill_fit


def button_models(patient_data, updated_table):
    col1, col2 = st.columns([2, 2])

    with col1:
        button_sigmoid_model(patient_data, updated_table)
    with col2:
        button_hill_model(patient_data, updated_table)

def button_sigmoid_model(patient_data, updated_table):
    # Filter selected and deselected data
    
    selected_data = patient_data[updated_table["Include in model"]]
    deselected_data = patient_data[~updated_table["Include in model"]]

    if not selected_data.empty:
        x_selected = selected_data["Insp. O2 (%)"].values
        y_selected = selected_data["SpO2 (%)"].values
        measurement_numbers_selected = selected_data["Measurement Nr"].values

        try:
            popt = train_sigmoid_model(x_selected, y_selected)
            fig, mse = plot_sigmoid_fit(x_selected, y_selected, popt, deselected_data, measurement_numbers_selected)
            
            st.pyplot(fig)
            st.write(f"Sigmoid Mean Squared Error (MSE): {mse:.4f}")
        except Exception as e:
            st.error(f"Error in fitting sigmoid model: {e}")
    else:
        st.warning("No data points selected for fitting the model.")


def button_hill_model(patient_data, updated_table):
    # Filter selected and deselected data
    selected_data = patient_data[updated_table["Include in model"]]
    deselected_data = patient_data[~updated_table["Include in model"]]

    if not selected_data.empty:
        x_selected = selected_data["Insp. O2 (%)"].values
        y_selected = selected_data["SpO2 (%)"].values
        measurement_numbers_selected = selected_data["Measurement Nr"].values

        try:
            popt = train_hill_model(x_selected, y_selected)
            fig, mse = plot_hill_fit(x_selected, y_selected, popt, deselected_data, measurement_numbers_selected)
            st.pyplot(fig)
            st.write(f" Hill Mean Squared Error (MSE): {mse:.4f}")
        except Exception as e:
            st.error(f"Error in fitting sigmoid model: {e}")
    else:
        st.warning("No data points selected for fitting the model.")