import numpy as np
import streamlit as st
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Define the sigmoid function
def sigmoid(x, L, x0, k, b):
    y = L / (1 + np.exp(-k * (x - x0))) + b
    return y

# Function to train the sigmoid model
def train_sigmoid_model(x_data, y_data):
    # Initial guess:
    #   L ~ (max(y) - min(y)), 
    #   x0 ~ mean(x),
    #   k ~ 0.1,
    #   b ~ min(y)
    p0 = [max(y_data) - min(y_data), np.mean(x_data), 0.1, min(y_data)]
    
    # Bounds: L in [0, 100], b in [0, 100], 
    # x0 unbounded, k >= 0
    # (Adjust as suits your data range.)
    bounds = (
        [0.0,       -np.inf,  0.0, 0.0],   # lower
        [100.0,      np.inf,  np.inf, 100.0]  # upper
    )
    
    popt, pcov = curve_fit(
        sigmoid, 
        x_data, 
        y_data, 
        p0=p0, 
        method='trf', 
        bounds=bounds
    )
    return popt


# Function to generate sigmoid curve and calculate MSE
def generate_sigmoid_fit(x_data, y_data, popt):
    if popt is None:
        raise ValueError("Sigmoid model parameters (`popt`) are not provided.")
    
    x_range = np.linspace(x_data.min() - 1, x_data.max() + 1, 100)
    y_fitted = sigmoid(x_range, *popt)
    y_pred = sigmoid(x_data, *popt)
    mse = np.mean((y_data - y_pred) ** 2)
    return x_range, y_fitted, mse

# Function to create a plot with sigmoid fit and data points
def plot_sigmoid_fit(x_selected, y_selected, popt, deselected_data=None, measurement_numbers_selected=None):
    x_range, y_fitted, mse = generate_sigmoid_fit(x_selected, y_selected, popt)

    fig, ax = plt.subplots()

    # Plot selected data points with labels
    if measurement_numbers_selected is not None:
        for i, (x, y, label) in enumerate(zip(x_selected, y_selected, measurement_numbers_selected)):
            ax.scatter(x, y, color="blue", label="Selected Data" if i == 0 else "")
            ax.text(x, y + 0.5, f"{label}", fontsize=10, ha="center", color="blue", fontweight="bold")

    # Plot deselected data points (if provided)
    if deselected_data is not None:
        for i, (x, y, label) in enumerate(zip(
            deselected_data["Insp. O2 (%)"], deselected_data["SpO2 (%)"], deselected_data["Measurement Nr"]
        )):
            ax.scatter(x, y, color="grey", label="Deselected Data" if i == 0 else "", alpha=0.6)
            ax.text(x, y + 0.5, f"{label}", fontsize=10, ha="center", color="grey", fontweight="bold")

    # Plot the fitted sigmoid curve
    ax.plot(x_range, y_fitted, color="red", label="Fitted Sigmoid")
    ax.set_title(f"Sigmoid Fit (MSE: {mse:.4f})")
    ax.set_xlabel("Insp. O2 (%)")
    ax.set_ylabel("SpO2 (%)")
    ax.legend()
    
    return fig, mse
