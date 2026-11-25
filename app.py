import streamlit as st
import joblib
import json
import os

st.set_page_config(
    page_title="DozAI - Smart Home AI",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 DozAI")
st.subheader("Smart Home Energy & Sleep Prediction")

# Load models
energy_model = joblib.load("models/xgb_energy.joblib")
sleep_model = joblib.load("models/sleep_xgb.joblib")

st.success("AI Models Loaded Successfully")

# Navigation
page = st.sidebar.selectbox(
    "Select Module",
    ["Home", "Energy Prediction", "Sleep Prediction", "Model Results"]
)

if page == "Home":
    st.title("Welcome to DozAI")
    st.write("AI-powered Smart Home Energy and Sleep Analysis.")

    col1, col2 = st.columns(2)
    col1.metric("AI Models", "2")
    col2.metric("Platform", "Machine Learning")

elif page == "Energy Prediction":
    st.header("Energy Prediction")
    st.info("Energy model loaded successfully.")

elif page == "Sleep Prediction":
    st.header("Sleep Prediction")
    st.info("Sleep model loaded successfully.")

elif page == "Model Results":
    st.header("Model Performance")

    with open("models/results.json", "r") as file:
        results = json.load(file)

    st.json(results)