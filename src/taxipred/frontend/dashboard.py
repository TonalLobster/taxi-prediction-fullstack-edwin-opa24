import streamlit as st
from taxipred.utils.helpers import read_api_endpoint
import pandas as pd
import requests

# --- Page configuration ---
st.set_page_config(
    page_title = "Taxi Fare Prediction Dashboard",
    page_icon = "🚕",
    layout = "centered",
)

# --- API URL ---
API_URL = "http://127.0.0.1:8000/predict"

# --- Page title ---
st.title("Estimate the price of your taxi trip")
st.markdown("Enter your start and end destination to get a estimated price for ytour trip")

# --- Step 1: User input for trip ---
st.header("1. Plan your trip")
col1,col2 = st.columns(2)
with col1:
    start_location = st.text_input("Where are you?", "Centralstationen, Borås")
with col2:
    end_location = st.text_input("Where to?", "Liseberg, Göteborg")

passenger_count = st.slider("Number of Passengers", 1, 4, 1)

# --- Step 2: Simulated "Smart" Data ---
st.header("2. Trip Conditions")
st.markdown("In the real app, this information would be fetched automatically!")

trip_distance_km = st.slider("Trip Distance (km)", 0.1, 150.0, 4.5, 0.1)
trip_duration_minutes = st.slider("Trip Duration (minutes)", 1.0, 120.0, 12.0, 1.0)

# boxes for other auto-detected data
col3, col4, col5 = st.columns(3)
with col3:
    day_of_week = st.selectbox("Day", ["Weekday", "Weekend"])
with col4:
    time_of_day = st.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night"])
with col5:
    traffic_conditions = st.selectbox("Traffic", ["Low", "Medium", "High"])
weather = st.selectbox("Weather Conditions", ["Clear", "Rain", "Snow"])

# --- step 3: Prediction ---
st.markdown("---")
if st.button("Calculate Price", type="primary", use_container_width=True):
    payload = {
        "Trip_Distance_km": trip_distance_km,
        "Time_of_Day": time_of_day,
        "Day_of_Week": day_of_week,
        "Passenger_Count": passenger_count,
        "Traffic_Conditions": traffic_conditions,
        "Weather": weather,
        "Base_Fare": 3.5, # example value
        "Per_Km_Rate": 1.5, # exapmle value
        "Per_Minute_Rate": 0.4, # example value
        "Trip_Duration_Minutes": trip_duration_minutes,
    }
    
    try:
        with st.spinner("Calculating your price..."):
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            prediction = response.json()
            price = prediction.get("predicted_price")

            st.success(f"## Estimated Fare: ${price:.2f}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the API. Please make sure the backend is running. Error: {e}")









data = read_api_endpoint("taxi")

df = pd.DataFrame(data.json())


def main():
    st.markdown("# Taxi Prediction Dashboard")

    st.dataframe(df)


if __name__ == "__main__":
    main()