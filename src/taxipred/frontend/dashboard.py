import streamlit as st
import pandas as pd
import requests

# --- Page configuration ---
st.set_page_config(
    page_title = "Taxi Fare Prediction Dashboard",
    page_icon = "🚕",
    layout = "wide",
)

# --- API URL ---
SMART_API_URL = "http://127.0.0.1:8000/smart_predict"

# Hardcoded example Coordinates for map visualization
GOTHENBURG_C_COORDS = (57.7088, 11.9745)
LISEBERG_COORDS = (57.6975, 12.0301)

# Sidebar setup ( business rules for product owner/admin)
with st.sidebar:
    st.header("⚙️ Business Rules (Product Owner Settings)")
    st.markdown("Adjust the base fare and rates to see the immediate impact on the prediction.")

    custom_base_fare = st.number_input("Base Fare ($)", min_value=1.0, value=3.5, step=0.1)
    custom_per_km_rate = st.number_input("Rate Per km ($)", min_value=0.5, value=1.5, step = 0.05)
    custom_per_minute_rate = st.number_input("Rate Per Minute ($)", min_value=0.1, value=0.4, step=0.05)

    st.markdown("---")



# --- Main Page Content ---
st.title("Resekollen AB: Smart Fare Estimator")
st.markdown("Enter your trip details to get a estimated price for ytour trip")

# --- User input for trip ---
st.header("1. Plan your trip")
col1,col2,col3 = st.columns(3)
with col1:
    start_location = st.text_input("Where are you?", "Centralstationen, Borås")
with col2:
    end_location = st.text_input("Where to?", "Liseberg, Göteborg")
with col3:
    # Passenger Input
    passenger_count = st.slider("Number of Passengers", 1, 4, 1)

# --- Prediction Button and Logic ---
if st.button("Calculate Price", type ="primary", use_container_width=True):
    payload = {
        "start_location": start_location,
        "end_location": end_location,
        "passenger_count": passenger_count,
        "base_fare": custom_base_fare,
        "per_km_rate": custom_per_km_rate,
        "per_minute_rate": custom_per_minute_rate
    }

    try:
        with st.spinner("Calculating distance, traffic and price..."):
            response = requests.post(SMART_API_URL, json=payload)
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                st.session_state.error = result["error"]
                st.session_state.price = None
            else:
                # Store results in session_state for display
                st.session_state.price = result.get("predicted_price")
                st.session_state.distance = result.get("calculated_distance_km")
                st.session_state.duration = result.get("calculated_duration_minutes")
                st.session_state.start_loc = start_location
                st.session_state.end_loc = end_location
                st.session_state.error = None
    except requests.exceptions.RequestException as e:
        "Error if the FastAPI server is down"
        st.session_state.error = f"Could not connect tot the API: {e}. Is it running?"
        st.session_state.price = None

# display results
if "error" in st.session_state and st.session_state.error:
    st.error(st.session_state.error)

elif "price" in st.session_state and st.session_state.price is not None:
    st.header("Your Estimate")
    col_res1, col_res2, col_res3 = st.columns(3)

    with col_res1:
        st.metric("Estimated Fare", f"${st.session_state.price:.2f}", delta_color="off")
    with col_res2:
        st.metric("Distance", f"{st.session_state.distance:.2f} km")
    with col_res3:
        st.metric("Travel Time", f"{st.session_state.duration:.0f} min")
    

    # simulated map for visual appeal
    st.subheader("Simulated Route visualizer")
    st.markdown("Shows general locations for visual effect)")

    # DataFrame for the map
    map_data = pd.DataFrame({
        "lat": [GOTHENBURG_C_COORDS[0], LISEBERG_COORDS[0]],
        "lon": [GOTHENBURG_C_COORDS[1], LISEBERG_COORDS[1]],
        "label": ["Start", "End"]
    })

    st.map(map_data, zoom=12)


