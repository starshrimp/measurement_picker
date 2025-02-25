import numpy as np
import streamlit as st
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Hill equation
def hill_eq(x, L, K, n):
    return L * (x**n / (K**n + x**n))

# Function to train the Hill model
def train_hill_model(x_data, y_data):
    # Initial guesses: L ~ max(y), K near mid of x, n ~ 1-3
    p0 = [100, 20, 2]  # example initial guess
    lower_bounds = [80,  1,   0.1]  # can be adjusted
    upper_bounds = [100, 40,  10]

    popt, pcov = curve_fit(
        hill_eq,
        x_data,
        y_data,
        p0=p0,
        bounds=(lower_bounds, upper_bounds),
        method='trf'
    )
    return popt

# Function to generate Hill fit and calculate MSE
def generate_hill_fit(x_data, y_data, popt):
    if popt is None:
        raise ValueError("Hill model parameters (`popt`) are not provided.")
    
    x_range = np.linspace(x_data.min() - 1, x_data.max() + 1, 100)
    y_fitted = hill_eq(x_range, *popt)
    y_pred = hill_eq(x_data, *popt)
    mse = np.mean((y_data - y_pred) ** 2)
    return x_range, y_fitted, mse

# Function to create a plot with Hill fit and data points
def plot_hill_fit(x_selected, y_selected, popt, deselected_data=None, measurement_numbers_selected=None):
    x_range, y_fitted, mse = generate_hill_fit(x_selected, y_selected, popt)

    fig, ax = plt.subplots()

    # Plot selected data points with labels
    if measurement_numbers_selected is not None:
        for i, (x, y, label) in enumerate(zip(x_selected, y_selected, measurement_numbers_selected)):
            ax.scatter(x, y, color="blue", label="Selected Data" if i == 0 else "")
            ax.text(x, y + 0.5, f"{label}", fontsize=10, ha="center", color="blue", fontweight="bold")

    # Plot deselected data points (if provided)
    if deselected_data is not None:
        for i, (x, y, label) in enumerate(zip(
            deselected_data["Insp. O2 (%)"], 
            deselected_data["SpO2 (%)"], 
            deselected_data["Measurement Nr"]
        )):
            ax.scatter(x, y, color="grey", label="Deselected Data" if i == 0 else "", alpha=0.6)
            ax.text(x, y + 0.5, f"{label}", fontsize=10, ha="center", color="grey", fontweight="bold")

    # Plot the fitted Hill curve
    ax.plot(x_range, y_fitted, color="red", label="Fitted Hill Curve")
    ax.set_title(f"Hill Fit (MSE: {mse:.4f})")
    ax.set_xlabel("Insp. O2 (%)")
    ax.set_ylabel("SpO2 (%)")
    ax.legend()
    
    return fig, mse

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
            st.write(f"Mean Squared Error (MSE): {mse:.4f}")
        except Exception as e:
            st.error(f"Error in fitting sigmoid model: {e}")
    else:
        st.warning("No data points selected for fitting the model.")