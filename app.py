
import streamlit as st
import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="DozAI - Smart Home AI",
    page_icon="🏠",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

st.title("🏠 DozAI")
st.subheader("Smart Home Energy & Sleep Prediction")
st.caption("AI-powered Smart Home Intelligence Platform")

# ---------------- LOAD MODELS ----------------
@st.cache_resource
def load_models():
    energy = joblib.load(MODEL_DIR / "xgb_energy.joblib")
    sleep = joblib.load(MODEL_DIR / "sleep_xgb.joblib")
    return energy, sleep

try:
    energy_model, sleep_model = load_models()
except Exception as e:
    st.error(f"Model loading error: {e}")
    st.stop()

st.success("Both AI models loaded successfully!")

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Energy Prediction", "Sleep Prediction", "Model Results"]
)

# ---------------- HOME ----------------
if page == "Home":

    st.header("Welcome to DozAI")

    st.write(
        "DozAI uses Machine Learning to forecast household "
        "energy consumption and estimate sleep quality."
    )

    col1, col2 = st.columns(2)

    col1.metric("AI Models", "2")
    col2.metric("Prediction Engine", "XGBoost")

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("⚡ Energy Intelligence")
        st.write("Predict household electricity consumption using:")
        st.write("- Previous 24, 48 and 168-hour consumption")
        st.write("- Temperature and heating demand")
        st.write("- Time and day information")

    with c2:
        st.subheader("😴 Sleep Intelligence")
        st.write("Estimate sleep quality using:")
        st.write("- Bedtime deviation")
        st.write("- Temperature and noise")
        st.write("- Stress and previous sleep quality")

# ---------------- ENERGY PREDICTION ----------------
elif page == "Energy Prediction":

    st.header("⚡ Energy Consumption Prediction")
    st.write("Enter household energy and weather information.")

    with st.form("energy_form"):

        col1, col2 = st.columns(2)

        with col1:
            kw_l24 = st.number_input(
                "Energy consumption 24 hours ago (kW)",
                min_value=0.0, value=0.8, step=0.1
            )

            kw_l48 = st.number_input(
                "Energy consumption 48 hours ago (kW)",
                min_value=0.0, value=0.8, step=0.1
            )

            kw_l168 = st.number_input(
                "Energy consumption 168 hours ago (kW)",
                min_value=0.0, value=0.8, step=0.1
            )

            kw_r24 = st.number_input(
                "Previous 24-hour average (kW)",
                min_value=0.0, value=0.8, step=0.1
            )

        with col2:
            temp_out = st.number_input(
                "Outside temperature (°C)",
                value=20.0, step=0.5
            )

            hour = st.slider("Hour of day", 0, 23, 18)

            dow = st.selectbox(
                "Day of week",
                options=list(range(7)),
                format_func=lambda x: [
                    "Monday", "Tuesday", "Wednesday",
                    "Thursday", "Friday", "Saturday", "Sunday"
                ][x]
            )

        submitted = st.form_submit_button(
            "Predict Energy Consumption",
            use_container_width=True
        )

    if submitted:

        hdd = max(15.0 - temp_out, 0.0)

        peak_hour = hour in list(range(7, 10)) + list(range(18, 22))
        hdd_peak = hdd * float(peak_hour)

        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)

        energy_input = pd.DataFrame([{
            "kw_l24": kw_l24,
            "kw_l48": kw_l48,
            "kw_l168": kw_l168,
            "kw_r24": kw_r24,
            "hdd": hdd,
            "hdd_peak": hdd_peak,
            "hour_sin": hour_sin,
            "hour_cos": hour_cos,
            "dow": dow
        }])

        try:
            prediction = float(energy_model.predict(energy_input)[0])

            st.divider()
            st.subheader("Energy Prediction Result")

            st.metric(
                "Predicted Energy Consumption",
                f"{max(prediction, 0):.3f} kW"
            )

            st.caption(
                "Prediction is generated using your trained XGBoost energy model."
            )

        except Exception as e:
            st.error(f"Prediction error: {e}")

# ---------------- SLEEP PREDICTION ----------------
elif page == "Sleep Prediction":

    st.header("😴 Sleep Quality Prediction")
    st.write("Enter your sleep, environment and lifestyle information.")

    with st.form("sleep_form"):

        col1, col2 = st.columns(2)

        with col1:
            bed_dev = st.number_input(
                "Bedtime deviation (hours)",
                min_value=-12.0, max_value=12.0,
                value=0.0, step=0.5
            )

            temp_at_bed = st.number_input(
                "Temperature at bedtime (°C)",
                value=18.5, step=0.5
            )

            noisy_prebed = st.number_input(
                "Pre-bed noise level (model input units)",
                min_value=0.0, value=5.0, step=1.0
            )

            stress = st.slider(
                "Stress level",
                min_value=1.0, max_value=10.0,
                value=5.0, step=0.5
            )

            dow_sleep = st.selectbox(
                "Day of week",
                options=list(range(7)),
                format_func=lambda x: [
                    "Monday", "Tuesday", "Wednesday",
                    "Thursday", "Friday", "Saturday", "Sunday"
                ][x],
                key="sleep_dow"
            )

        with col2:
            lag_q = st.number_input(
                "Previous day's sleep quality",
                min_value=5.0, max_value=100.0,
                value=70.0, step=1.0
            )

            lag_stress = st.number_input(
                "Previous day's stress",
                min_value=1.0, max_value=10.0,
                value=5.0, step=0.5
            )

            roll7_q = st.number_input(
                "Previous 7-day average sleep quality",
                min_value=5.0, max_value=100.0,
                value=70.0, step=1.0
            )

            standby_w = st.number_input(
                "Standby power (Watts)",
                min_value=0.0, value=100.0, step=5.0
            )

        submitted = st.form_submit_button(
            "Predict Sleep Quality",
            use_container_width=True
        )

    if submitted:

        sleep_input = pd.DataFrame([{
            "bed_dev": bed_dev,
            "temp_at_bed": temp_at_bed,
            "noisy_prebed": noisy_prebed,
            "stress": stress,
            "lag_q": lag_q,
            "lag_stress": lag_stress,
            "roll7_q": roll7_q,
            "standby_w": standby_w,
            "dow": dow_sleep
        }])

        try:
            prediction = float(sleep_model.predict(sleep_input)[0])
            prediction = float(np.clip(prediction, 5, 100))

            st.divider()
            st.subheader("Sleep Prediction Result")

            st.metric(
                "Predicted Sleep Quality",
                f"{prediction:.2f} / 100"
            )

            st.progress(prediction / 100)

            if prediction >= 80:
                st.success("Good predicted sleep quality")
            elif prediction >= 60:
                st.info("Moderate predicted sleep quality")
            else:
                st.warning("Low predicted sleep quality")

            st.caption(
                "This is a model-based estimate, not a medical assessment."
            )

        except Exception as e:
            st.error(f"Prediction error: {e}")

# ---------------- MODEL RESULTS ----------------
elif page == "Model Results":

    st.header("📊 Model Performance")

    results_file = MODEL_DIR / "results.json"

    if results_file.exists():

        try:
            with open(results_file, "r", encoding="utf-8") as file:
                results = json.load(file)

            st.json(results)

        except Exception as e:
            st.error(f"Unable to read results.json: {e}")

    else:
        st.warning("models/results.json was not found.")

    st.divider()
    st.subheader("Loaded Model Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Energy Model**")
        st.write("Algorithm: XGBoost Regressor")
        st.write("Input features:", energy_model.n_features_in_)

    with col2:
        st.write("**Sleep Model**")
        st.write("Algorithm: XGBoost Regressor")
        st.write("Input features:", sleep_model.n_features_in_)

# ---------------- FOOTER ----------------
st.divider()
st.caption("DozAI | Smart Home Energy & Sleep Intelligence")
