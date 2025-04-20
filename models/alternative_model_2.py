import mlflow
import mlflow.lightgbm
from mlflow.models import infer_signature
import numpy as np
import pandas as pd
from operator import itemgetter
import sqlalchemy
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFE
import lightgbm as lgb  # Import LightGBM
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
import scipy.stats as stats
import joblib
import os

# Collecting data from database housing_db
engine = sqlalchemy.create_engine("mysql+pymysql://root:root@localhost:3307/housing_db")
df = pd.read_sql("SELECT * FROM housing_data", engine)

print(df.dtypes)

df_subset = df.drop(columns=['id', 'block', 'street', 'scraped_date', 'scraped_month', 'scraped_year'])

print(df_subset.dtypes)

# Apply One-Hot Encoding
df_subset = pd.get_dummies(df_subset, columns=['n_rooms', 'district', 'region', 'area', 'n_bedrooms', 'n_bathrooms'], drop_first=True, dtype=int)

# Apply Label Encoding to 'is_central' and 'is_mature_town'
label_encoder = LabelEncoder()
df_subset['is_central'] = label_encoder.fit_transform(df_subset['is_central'])
df_subset['is_mature_town'] = label_encoder.fit_transform(df_subset['is_mature_town'])

# Now, perform feature selection after encoding
columns_to_drop = ['price', 'price_per_sqft', 'price_per_bedroom', 'lease_price_interaction']
X = df_subset.drop(columns_to_drop, axis=1)  # Features

Y = df_subset['price']  # Target
print(X)
print(X.dtypes)

# Feature selection using RFE
estimator = lgb.LGBMRegressor()  # Use LightGBM regressor
selector = RFE(estimator, n_features_to_select=20)
selector.fit(X, Y)

# Get the selected features from RFE
selected_features = X.columns[selector.support_]
print("Selected features:", selected_features)
# Get absolute path to this script's folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build absolute path to target directory
output_dir = os.path.join(BASE_DIR, "../api/models_dump_for_Registry")
os.makedirs(output_dir, exist_ok=True)

joblib.dump(selected_features.tolist(), os.path.join(output_dir, "selected_features.joblib"))

# Train-test split
X_selected = X[selected_features]
X_train, X_test, y_train, y_test = train_test_split(X_selected, Y, test_size=0.30, random_state=42)

# Scaling the numerical features using StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Fit and transform on training data
X_test_scaled = scaler.transform(X_test)  # Only transform test data (do not fit again)
#joblib.dump(scaler, "../api/models_dump_for_Registry/scaler.joblib")
joblib.dump(scaler, os.path.join(output_dir, "scaler.joblib"))

# Set tracking URI for MLflow
mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")  # Local server URI
mlflow.set_experiment("LightGBM Model")  # Log experiment name

# Start MLflow run for model training
with mlflow.start_run(run_name="Alternative Model 2 - LightGBM Model"):
    model = lgb.LGBMRegressor()  # LightGBM regressor
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    # Calculate metrics
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))  # RMSE calculation
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    average_price = np.mean(y_test)
    mae_percent = (mae / average_price) * 100
    rmse_percent = (rmse / average_price) * 100

    # Log parameters, metrics, and model
    mlflow.log_param("model_type", "LightGBM")
    mlflow.log_metric("Root Mean Squared Error", rmse)
    mlflow.log_metric("Mean Absolute Error", mae)
    mlflow.log_metric("R-squared error", r2)
    mlflow.log_metric("Relative error of RMSE to Average house prices", rmse_percent)
    mlflow.log_metric("Relative error of MAE to Average house prices", mae_percent)

    # Set a tag to identify the experiment run
    mlflow.set_tag("Training Info", "Alternative Model - LightGBM Model")

    # Infer the model signature
    signature = infer_signature(X_test_scaled, model.predict(X_test_scaled))

    # Log the model
    model_info = mlflow.lightgbm.log_model(
        lgb_model=model,  # Corrected argument name
        artifact_path="lightgbm_model",
        signature=signature,
        input_example=X_test_scaled,
        registered_model_name="lightgbm_model"
    )

    print(f"Model URI: {model_info.model_uri}")
    print(f"Run ID: {model_info.run_id}")
    print(f"Artifact path: {model_info.artifact_path}") 

    # Calculate residuals (differences between actual and predicted values)
    residuals = y_test - y_pred

    # Estimate the standard deviation of residuals
    std_residuals = np.std(residuals)

    # Calculate the 95% confidence interval using the standard normal distribution
    # For 95% confidence, the z-score for a two-tailed test is approximately 1.96
    confidence_interval = 1.96 * std_residuals

    # Predict the 95% prediction interval for each house price
    lower_bound = y_pred - confidence_interval
    upper_bound = y_pred + confidence_interval

    X_test['Predicted Price'] = y_pred
    X_test['Lower Bound'] = lower_bound
    X_test['Upper Bound'] = upper_bound
    # Print the model URI
    print(model_info.model_uri)


X_test.to_csv('TEST.csv', index=False)
