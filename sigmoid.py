import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Define the sigmoid function
def sigmoid(x, a, b, c):
    return c / (1 + np.exp(-(x - a) / b))

# Function to train the sigmoid model
def train_sigmoid_model(x_data, y_data):
    popt, _ = curve_fit(sigmoid, x_data, y_data, maxfev=10000)
    return popt

# Function to generate sigmoid curve and calculate MSE
def generate_sigmoid_fit(x_data, y_data, popt):
    if popt is None:
        raise ValueError("Sigmoid model parameters (`popt`) are not provided.")
    
    x_range = np.linspace(x_data.min(), x_data.max(), 100)
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
