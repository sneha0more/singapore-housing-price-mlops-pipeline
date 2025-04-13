# predictor.py

import os
import mlflow.pyfunc
from mlflow.tracking import MlflowClient
import joblib
import pandas as pd

MODEL_NAME = "lightgbm_model"
mlflow.set_tracking_uri("http://127.0.0.1:5000")

print("✅ Fetching model from registry...")

client = MlflowClient()
latest_versions = client.search_model_versions(f"name='{MODEL_NAME}'")

if not latest_versions:
    raise ValueError(f"No model versions found for model '{MODEL_NAME}'.")

# Pick highest version
latest = sorted(latest_versions, key=lambda v: int(v.version), reverse=True)[0]
model_uri = f"runs:/{latest.run_id}/{latest.source.split('/')[-1]}"

# 🔥 This is where you use the model URI!
try:
    model = mlflow.pyfunc.load_model(model_uri)
    selected_features = joblib.load("models_dump_for_Registry/selected_features.joblib")
    scaler = joblib.load("models_dump_for_Registry/scaler.joblib")
except Exception as e:
    print("❌ Error loading model or files:", e)

def predict_price(user_input_df):
    # Ensure columns match and are in order
    X_selected = user_input_df[selected_features]
    X_scaled = scaler.transform(X_selected)
    X_scaled_df = pd.DataFrame(X_scaled, columns=selected_features)

    # Predict
    preds = model.predict(X_scaled_df)
    return preds[0]
