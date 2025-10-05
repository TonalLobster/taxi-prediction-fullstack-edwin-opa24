from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData
import joblib
import pandas as pd
from pydantic import BaseModel
import googlemaps
import datetime
import os
from dotenv import load_dotenv


# Configuration
# Load in variables from .env file for safe use of keys and secrets
load_dotenv()
GMAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# --- Pydantic model for input-data ---
class SimpleTrip(BaseModel):
    start_location: str
    end_location: str
    passenger_count: float
    base_fare: float
    per_km_rate: float
    per_minute_rate: float


# --- Application-setup ---
app = FastAPI(
    title="Taxi Price Prediction API",
    description="An API to predict taxi trip prices with a RandomForest-model.",
    version="0.1.1",
)


# Load the trained ML-model
model_path = "src/taxipred/backend/models/random_forest_final.joblib"
model = joblib.load(model_path)


# Load the original data for the taxi endpooint
taxi_data = TaxiData()

# Initialize Google Maps Client
gmaps = googlemaps.Client(key=GMAPS_API_KEY)

# Helper functions
def get_traffic_status(duration_in_seconds):
    # Simple logic based on expected travel time for a typical city trip
    if duration_in_seconds > 45 * 60:
        return "High"
    elif duration_in_seconds > 20 * 60:
        return "Medium"
    else:
        return "Low"


# --- API Endpoints ---

@app.get("/taxi")
async def read_taxi_data():
    # endpoint to fetch a sample of the original taxi data.
    return taxi_data.to_json()


@app.post("/smart_predict")
async def smart_predict_price(trip: SimpleTrip):
    
    """
    Endpoint that uses Google maps Directions API for accurate distance and time,
    then constructs trhe full feature set for the ML model.
    """
    if not GMAPS_API_KEY:
        return {"error": "Google Mapi API Key not loaded from .env file."}
    try:
        # 1. Call google Maps Directions API to get distance and time.
        directions_result = gmaps.directions(
            trip.start_location,
            trip.end_location,
            mode="driving",
            departure_time = "now"

        )
        if not directions_result:
            return {"error": "Could not find a route between the locations. Please be more specific with your adresses."}
        
        # Extract data from the first route leg
        route = directions_result[0]["legs"][0]
        # get latitude and longitude fro map
        start_lat = route["start_location"]["lat"]
        start_lon = route["start_location"]["lng"]
        end_lat = route["end_location"]["lat"]
        end_lon = route["end_location"]["lng"]
        distance_km = route["distance"]["value"] / 1000
        # Use duration with traffic for predition accuracy
        duration_seconds = route["duration_in_traffic"]["value"] if "duration_in_traffic" in route else route["duration"]["value"]
        trip_duration_minutes = duration_seconds / 60

        # 2. Determine Time and traffic factors
        now = datetime.datetime.now()
        day_of_week = "Weekend" if now.weekday() >= 5 else "Weekday"

        current_hour = now.hour
        time_of_day = "Morning" if 6 <= current_hour < 12 else "Afternoon" if 12 <= current_hour < 18 else "Evening"
        
        traffic_conditions = get_traffic_status(duration_seconds)
        weather = "Clear" 

        # 3. Create DataFrame for the ML model
        input_data = pd.DataFrame([{
            "Trip_Distance_km": distance_km,
            "Time_of_Day": time_of_day,
            "Day_of_Week": day_of_week,
            "Passenger_Count": trip.passenger_count,
            "Traffic_Conditions": traffic_conditions,
            "Weather": weather,
            # business rules passed from the frontend
            "Base_Fare": trip.base_fare,
            "Per_Km_Rate": trip.per_km_rate,
            "Per_Minute_Rate": trip.per_minute_rate,
            "Trip_Duration_Minutes": trip_duration_minutes
        }])

        # 4. preprocess, predict and return
        input_processed = pd.get_dummies(input_data)
        model_columns = model.feature_names_in_
        input_processed = input_processed.reindex(columns=model_columns, fill_value=0)

        prediction = model.predict(input_processed)
        return {
            "predicted_price": round(prediction[0], 2),
            "calculated_distance_km": round(distance_km, 2),
            "calculated_duration_minutes": round(trip_duration_minutes, 2),
            "start_lat": start_lat,
            "start_lon": start_lon,
            "end_lat": end_lat,
            "end_lon": end_lon,
        }
    
    except Exception as e:
        return {"error": f"An unexcpected error occurred during API call:{e}"}
