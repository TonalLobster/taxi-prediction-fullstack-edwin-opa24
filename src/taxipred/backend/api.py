from fastapi import FastAPI
from taxipred.backend.data_processing import TaxiData
import joblib
import pandas as pd
from pydantic import BaseModel


# --- Pydantic model for input-data ---
# Define exactly what data our predict endpoint is expecting.
class TaxiTrip(BaseModel):
    Trip_Distance_km: float
    Time_of_Day: str
    Day_of_Week: str
    Passenger_Count: float
    Traffic_Conditions: str
    Weather: str
    Base_Fare: float
    Per_Km_Rate: float
    Per_Minute_Rate: float
    Trip_Duration_Minutes: float


# --- Application-setup ---
app = FastAPI(
    title="Taxi Price Prediction API",
    description="An API to predict taxi trip prices with a RandomForest-model.",
    version="0.1.0",
)


# Load the trained ML-model
model_path = "src/taxipred/backend/models/random_forest_final.joblib"
model = joblib.load(model_path)


# Load the original data for the taxi endpooint
taxi_data = TaxiData()


# --- API Endpoints ---

@app.get("/taxi")
async def read_taxi_data():
    # endpoint to fetch a sample of the original taxi data.
    return taxi_data.to_json()


@app.post("/predict")
async def predict_price(trip: TaxiTrip):
    """
    Endpoint to predict the price of a taxi trip.

    Send a JSON object with the trip details to get an estimated pricee.
    """
    # 1. Convert the incoming data from the user into a pandas DataFrame
    input_data = pd.DataFrame([trip.model_dump()])

    # 2. convert text columns to numverical "Dummy" columns, just like the notebook
    input_processed = pd.get_dummies(input_data)

    # 3. Ensure the input data has the exact same columns as the moidel was trained on
    # This is a critical step to avoid errors if a category is missing.

    model_columns = model.feature_names_in_
    input_processed = input_processed.reindex(columns=model_columns, fill_value=0)

    # 4. use the loaded model to make a prediction
    prediction = model.predict(input_processed)

    # 5. return the prediction, rounded to 2 decimals in a JSON response
    return {"predicted_price": round(prediction[0], 2)}
