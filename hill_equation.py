import numpy as np
import streamlit as st
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Hill equation
def hill_eq(x, L, K, n):
    return L * (x**n / (K**n + x**n))

# Function to train the Hill model
def train_hill_model(x_data, y_data):
    # Updated initial guesses and tighter bounds for improved fitting
    p0 = [90, 15, 1.5]
    lower_bounds = [80, 10, 0]
    upper_bounds = [100, 35, 10]

    
    try:
        popt, pcov = curve_fit(
            hill_eq,
            x_data,
            y_data,
            p0=p0,
            bounds=(lower_bounds, upper_bounds),
            method='trf'
        )
        return popt
    except Exception as e:
        st.error(f"Error in curve fitting: {e}")
        return None

# Function to generate Hill fit and calculate MSE
def generate_hill_fit(x_data, y_data, popt):
    if popt is None:
        raise ValueError("Hill model parameters (`popt`) are not provided.")
    # Using more points for a smoother curve
    x_range = np.linspace(x_data.min() - 1, x_data.max() + 1, 500)
    y_fitted = hill_eq(x_range, *popt)
    y_pred = hill_eq(x_data, *popt)
    mse = np.mean((y_data - y_pred) ** 2)
    return x_range, y_fitted, mse




def plot_hill_fit(x_selected, y_selected, popt, deselected_data=None, measurement_numbers_selected=None):
    try:
        x_range, y_fitted, mse = generate_hill_fit(x_selected, y_selected, popt)
    except Exception as e:
        st.error(f"Error generating Hill fit: {e}")
        return None, None

    fig, ax = plt.subplots()

    selected_points = set(zip(x_selected, y_selected))

    # Plot selected data points with optional labels
    if measurement_numbers_selected is not None:
        for i, (x, y, label) in enumerate(zip(x_selected, y_selected, measurement_numbers_selected)):
            ax.scatter(x, y, color="blue", label="Selected Data" if i == 0 else "")
            ax.text(x, y + 0.5, f"{label}", fontsize=10, ha="center", color="blue", fontweight="bold")
    else:
        ax.scatter(x_selected, y_selected, color="blue", label="Selected Data")

    # Plot deselected data points if provided
    if deselected_data is not None:
        for i, (x, y, label) in enumerate(zip(
            deselected_data["Insp. O2 (%)"], 
            deselected_data["SpO2 (%)"], 
            deselected_data["Measurement Nr"]
        )):
            # Skip specific points (0,0) and (9.7,50) if they are deselected
            if (x, y) == (0, 0):
                continue
            if (x, y) == (9.7, 50) and (0, 0) in selected_points:
                pass  # Show as deselected
            elif (x, y) in [(9.7, 50), (0, 0)]:
                continue
            ax.scatter(x, y, color="grey", label="Deselected Data" if i == 0 else "", alpha=0.6)
            ax.text(x, y + 0.5, f"{label}", fontsize=10, ha="center", color="grey", fontweight="bold")

    # Plot the fitted Hill curve
    ax.plot(x_range, y_fitted, color="red", label="Fitted Hill Curve")
    ax.set_title(f"Hill Fit (MSE: {mse:.4f})")
    ax.set_xlabel("Insp. O2 (%)")
    ax.set_ylabel("SpO2 (%)")
    ax.legend()
    
    return fig, mse
