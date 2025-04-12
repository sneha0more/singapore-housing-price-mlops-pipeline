# predictor.py

import os
import mlflow.pyfunc
import joblib
import pandas as pd

# Set MLflow tracking URI
mlflow.set_tracking_uri("http://172.17.0.1:5000")

# Absolute paths within the container
model = mlflow.pyfunc.load_model("models:/lightgbm_model/Staging")
selected_features = joblib.load("/app/models/models_dump_for_Registry/selected_features.joblib")
scaler = joblib.load("/app/models/models_dump_for_Registry/scaler.joblib")


def predict_price(user_input_df):
    # Ensure columns match and are in order
    X_selected = user_input_df[selected_features]
    X_scaled = scaler.transform(X_selected)
    X_scaled_df = pd.DataFrame(X_scaled, columns=selected_features)

    # Predict
    preds = model.predict(X_scaled_df)
    return preds[0]
