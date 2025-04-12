print("✅ FastAPI app is starting...")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

@app.get("/")
def home():
    return {"message": "🏡 Housing Price Prediction API is live!"}



class InputData(BaseModel):
    build_year: int
    size_sqft: float
    n_bedrooms: int
    n_bathrooms: int
    area: str
    district: str
    region: str
    n_rooms: str

@app.post("/predict")
def predict(data: InputData):
    try:
        # Import inside the function to avoid crashing app during startup
        from .predictor import predict_price
        from .preprocessing import preprocess_user_input

        input_dict = data.dict()
        df_input = preprocess_user_input(input_dict)
        prediction = predict_price(df_input)

        return {
            "predicted_price": round(prediction, 2),
            "price_range": {
                "lower": round(prediction * 0.95, 2),
                "upper": round(prediction * 1.05, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
