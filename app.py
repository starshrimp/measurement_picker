import streamlit as st
import pandas as pd
import numpy as np
import scipy.optimize as opt
import os
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import mean_squared_error

def sigmoid(x, L, x0, k, b):
    return L / (1 + np.exp(-k * (x - x0))) + b

def fit_sigmoid(x_data, y_data):
    p0 = [max(y_data), np.median(x_data), 1, min(y_data)]
    popt, _ = opt.curve_fit(sigmoid, x_data, y_data, p0, method='dogbox')
    return popt

def loocv_mse(x_data, y_data):
    loo = LeaveOneOut()
    errors = []
    for train_index, test_index in loo.split(x_data):
        x_train, x_test = x_data[train_index], x_data[test_index]
        y_train, y_test = y_data[train_index], y_data[test_index]
        params = fit_sigmoid(x_train, y_train)
        y_pred = sigmoid(x_test, *params)
        errors.append(mean_squared_error(y_test, y_pred))
    return np.mean(errors)

# Load dataset
data_file = "/Users/sarah/ML/master_thesis/anonymized_patient_data_219.csv"
if os.path.exists(data_file):
    df = pd.read_csv(data_file)
else:
    st.error("Data file not found!")
    st.stop()

st.title("Patient Oxygen Saturation Visualization")

# Select patient ID
patient_ids = df["Anon_Patient_ID"].unique()
selected_patient = st.selectbox("Select Patient ID", patient_ids)

# Filter data for selected patient
patient_data = df[df["Anon_Patient_ID"] == selected_patient].copy()
patient_data["selected"] = 1

# Checkbox for each measurement
st.subheader(f"Measurements for Patient {selected_patient}")
checkboxes = []
for index, row in patient_data.iterrows():
    checked = st.checkbox(f"Insp. O2: {row['Insp. O2 (%)']}, SpO2: {row['SpO2 (%)']}", value=True, key=index)
    checkboxes.append(checked)

# Update selected values
patient_data["selected"] = [1 if c else 0 for c in checkboxes]

# Additional checkboxes for classification
st.subheader("Patient Classification")
ideal_curve = st.checkbox("Ideal Curve", value=False)
outlier = st.checkbox("Outlier", value=False)

# Train sigmoid model
if st.button("Train Sigmoid Model"):
    selected_data = patient_data[patient_data["selected"] == 1]
    if len(selected_data) > 2:
        x_data = selected_data["Insp. O2 (%)"].values
        y_data = selected_data["SpO2 (%)"].values
        params = fit_sigmoid(x_data, y_data)
        mse = loocv_mse(x_data, y_data)
        x_fit = np.linspace(min(x_data), max(x_data), 100)
        y_fit = sigmoid(x_fit, *params)

        st.subheader("Model Fit")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.scatter(x_data, y_data, color='blue', label='Selected Data')
        ax.scatter(patient_data["Insp. O2 (%)"], patient_data["SpO2 (%)"], color='grey', alpha=0.5, label='Deselected Data')
        ax.plot(x_fit, y_fit, color='red', label='Sigmoid Fit')
        ax.set_xlabel("Inspired O2 (%)")
        ax.set_ylabel("SpO2 (%)")
        ax.legend()
        st.pyplot(fig)
        
        st.subheader("Model Performance")
        st.write(f"Leave-One-Out Cross-Validation MSE: {mse:.5f}")
    else:
        st.warning("At least 3 data points must be selected to train the model.")

# Save settings and export CSV files
if st.button("Export Data"):
    patient_data.to_csv("measurements.csv", index=False)
    classification_data = pd.DataFrame({"Anon_Patient_ID": [selected_patient], "Ideal_Curve": [int(ideal_curve)], "Outlier": [int(outlier)]})
    classification_data.to_csv("patient_ideal_outlier.csv", mode='a', header=not os.path.exists("patient_ideal_outlier.csv"), index=False)
    st.success("Data exported successfully!")
