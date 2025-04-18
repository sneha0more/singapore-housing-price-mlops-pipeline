import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import RFE
from sklearn.model_selection import train_test_split
import datetime
import os


#BEST_RUN_ID = "1d9bef0f160b4d6583fc0b17138bbc09"  

# ------------ CONFIG ------------
MODEL_NAME = "lightgbm_model"
STAGE_TO_SET = "STAGING"  
#Model URI: runs:/d46c6cb9d0884eacbd654c81ebe40916/lightgbm_model
#Run ID: d46c6cb9d0884eacbd654c81ebe40916
#Artifact path: lightgbm_model
# ------------ INIT ------------
#mlflow.set_tracking_uri("http://localhost:5000")  # Update if using remote MLflow
mlflow.set_tracking_uri("http://127.0.0.1:5000")
#mlflow.lightgbm.log_model(..., registered_model_name="lightgbm_model")
print("Current tracking URI:", mlflow.get_tracking_uri())

client = MlflowClient()

# ------------ Fetch latest un-staged model version ------------

latest_versions = client.search_model_versions(f"name='{MODEL_NAME}'")
if not latest_versions:
    raise ValueError(f"No model versions found for model '{MODEL_NAME}' in 'None' stage.")

# Sort by version number (as int)
latest_versions_sorted = sorted(latest_versions, key=lambda v: int(v.version), reverse=True)

# Pick the highest version
latest = latest_versions_sorted[0]

#latest = latest_versions[0]  # Most recent version not yet staged
run_id = latest.run_id
version = latest.version
model_uri = f"runs:/{run_id}/{latest.source.split('/')[-1]}"

# ------------ Transition to STAGING ------------
client.transition_model_version_stage(
    name=MODEL_NAME,
    version=version,
    stage=STAGE_TO_SET,
    archive_existing_versions=True
)

# ------------ Add Tags ------------
today = datetime.date.today().isoformat()
client.set_model_version_tag(MODEL_NAME, version, "run_date", today)
client.set_model_version_tag(MODEL_NAME, version, "source_run_id", run_id)
client.set_model_version_tag(MODEL_NAME, version, "model_type", "lightgbm")

print(f"✅ Model '{MODEL_NAME}' version {version} promoted to '{STAGE_TO_SET}' and tagged.")


# Define model URI from the registry
model_uri = "models:/lightgbm_model/Staging" 

# Load the model
model = mlflow.pyfunc.load_model(model_uri)
print(f"Model loaded from registry.")
print(f"Model type: {type(model)}")
print(f"Model metadata: {model.metadata}")

# ------------------- STEP 4: Load data and get test subset -------------------
import pandas as pd
import joblib
import mlflow.pyfunc
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

selected_features_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../api/models_dump_for_Registry/selected_features.joblib"))
# Get absolute path to this script's folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Build absolute path to target directory
output_dir_1 = os.path.join(BASE_DIR, "../api/models_dump_for_Registry/selected_features.joblib")
output_dir_2 = os.path.join(BASE_DIR, "../api/models_dump_for_Registry/scaler.joblib")

# === Load saved assets ===
selected_features = joblib.load(output_dir_1)
scaler = joblib.load(output_dir_2)

# === Step 1: Load data from MySQL ===
engine = create_engine("mysql+pymysql://root:root@localhost:3307/housing_db")
df = pd.read_sql("SELECT * FROM housing_data", con=engine)

# === Step 2: Preprocess data ===
df = df.drop(columns=['id', 'block', 'street', 'scraped_date', 'scraped_month', 'scraped_year'])
df = pd.get_dummies(df, columns=['n_rooms', 'district', 'region', 'area', 'n_bedrooms', 'n_bathrooms'], drop_first=True, dtype=int)

le = LabelEncoder()
df['is_central'] = le.fit_transform(df['is_central'])
df['is_mature_town'] = le.fit_transform(df['is_mature_town'])

# === Step 3: Extract features and target ===
X = df.drop(columns=['price'])
y = df['price']

# === Step 4: Use saved selected features and split ===
X_selected = X[selected_features]
X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=0.30, random_state=42)

# === Step 5: Scale only test data ===
X_test_scaled = scaler.transform(X_test)
X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=selected_features)

# === Step 6: Load model from MLflow ===
mlflow.set_tracking_uri("http://127.0.0.1:5000")
model = mlflow.pyfunc.load_model("models:/lightgbm_model/Staging")

# === Step 7: Predict ===
preds = model.predict(X_test_scaled_df)

# === Step 8: Output results ===
results = pd.DataFrame({
    "Predicted Price": preds,
    "Actual Price": y_test.values
})

print("✅ Prediction on test set:")
print(results.head())

# Optional: Save to CSV
results.to_csv("predicted_test_only.csv", index=False)
