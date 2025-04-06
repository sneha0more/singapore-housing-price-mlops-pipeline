import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
import numpy as np
import pandas as pd
from operator import itemgetter
import sqlalchemy
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFE
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample

# Collecting data from database housing_db
engine = sqlalchemy.create_engine("mysql+pymysql://root:root@localhost:3306/housing_db")
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
X = df_subset.drop('price', axis=1)  # Features
Y = df_subset['price']  # Target
print(X)
print(X.dtypes)

# Feature selection using RFE
estimator = xgb.XGBRegressor()
#X_number = X.select_dtypes(include=['number']).copy()  # Only numerical features
selector = RFE(estimator, n_features_to_select=20)
selector.fit(X, Y)

# Get the selected features from RFE
selected_features = X.columns[selector.support_]
print("Selected features:", selected_features)

# Train-test split
X_selected = X[selected_features]
X_train, X_test, y_train, y_test = train_test_split(X_selected, Y, test_size=0.30, random_state=42)

# Scaling the numerical features using StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Fit and transform on training data
X_test_scaled = scaler.transform(X_test)  # Only transform test data (do not fit again)

# Set tracking URI for MLflow
mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")  # Local server URI
mlflow.set_experiment("XGBoost Model")  # Log experiment name

# Start MLflow run for model training
with mlflow.start_run(run_name="Baseline Model - XGBoost Model"):
    model = xgb.XGBRegressor()  # XGBoost regressor
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
    mlflow.log_param("model_type", "XGBoost")
    mlflow.log_metric("Root Mean Squared Error", rmse)
    mlflow.log_metric("Mean Absolute Error", mae)
    mlflow.log_metric("R-squared error", r2)
    mlflow.log_metric("Relative error of RMSE to Average house prices", rmse_percent)
    mlflow.log_metric("Relative error of MAE to Average house prices", mae_percent)

    # Set a tag to identify the experiment run
    mlflow.set_tag("Training Info", "Alternative Model - XGBoost Model")

    # Infer the model signature
    signature = infer_signature(X_test_scaled, model.predict(X_test_scaled))

    # Log the model
    model_info = mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="xgboost_model",
        signature=signature,
        input_example=X_test_scaled,
        registered_model_name="xgboost_model"
    )

    # Print the model URI
    print(model_info.model_uri)

# Function for calculating bootstrap-based prediction intervals
def bootstrap_prediction_interval(model, X_train, y_train, X_test, n_iterations=1000, confidence_level=0.95):
    predictions = np.zeros((n_iterations, X_test.shape[0]))

    # Bootstrap loop
    for i in range(n_iterations):
        # Bootstrap sample
        X_resampled, y_resampled = resample(X_train, y_train, random_state=i)
        
        # Fit model on resampled data
        model.fit(X_resampled, y_resampled)
        
        # Predict with resampled model
        predictions[i, :] = model.predict(X_test)

    # Calculate lower and upper quantiles (e.g., for 95% CI)
    lower_percentile = (1 - confidence_level) / 2 * 100
    upper_percentile = (1 + confidence_level) / 2 * 100
    
    lower_bound = np.percentile(predictions, lower_percentile, axis=0)
    upper_bound = np.percentile(predictions, upper_percentile, axis=0)
    
    return lower_bound, upper_bound

# Calculate the 95% prediction interval for the test set
lower_bound, upper_bound = bootstrap_prediction_interval(model, X_train_scaled, y_train, X_test_scaled)

# Add the predicted prices and the prediction interval bounds to the test DataFrame (before scaling)
X_test['Predicted Price'] = y_pred
X_test['Lower Bound'] = lower_bound
X_test['Upper Bound'] = upper_bound
