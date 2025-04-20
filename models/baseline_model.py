import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
import numpy as np
import pandas as pd 
from operator import itemgetter
import sqlalchemy
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFE
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.utils import resample
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score

# Collecting data from database housing_db
engine = sqlalchemy.create_engine("mysql+pymysql://root:root@localhost:3307/housing_db")
df = pd.read_sql("SELECT * FROM housing_data", engine)

df_subset = df.drop(columns=['id', 'block', 'street', 'scraped_date', 'scraped_month', 'scraped_year'])

columns_to_drop = ['price', 'price_per_sqft', 'price_per_bedroom', 'lease_price_interaction']
X = df_subset.drop(columns_to_drop, axis=1)  # Features

Y = df_subset['price']

# -------------- Feature Selection -------------------
# Feature selection using RFE
estimator = LinearRegression()
X_number = X.select_dtypes(include=['number']).copy()
selector = RFE(estimator, n_features_to_select=20)
selector.fit(X_number, Y)

# Get the selected features from RFE
selected_features = X_number.columns[selector.support_]
print("Selected features:", selected_features)

# Train-test split features
X_selected = X_number[selected_features]
X_train, X_test, y_train, y_test = train_test_split(X_selected, Y, test_size=0.30, random_state=42)

mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")  # Replace with host machine IP
mlflow.set_experiment("Linear Regression Model")   # Log experiment name

with mlflow.start_run(run_name="Baseline Model - Linear Regression Model"):
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Calculate metrics
    rmse = root_mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    average_price = np.mean(y_test)
    # To calculate relative error:
    mae_percent = (mae / average_price) * 100
    rmse_percent = (rmse / average_price) * 100

    # Log parameters, metrics, and model
    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_metric("Root Mean Squared Error", rmse)
    mlflow.log_metric("Mean Absolute Error", mae)
    mlflow.log_metric("R-squared error", r2)
    mlflow.log_metric("Relative error of RMSE to Average house prices", rmse_percent)
    mlflow.log_metric("Relative error of MAE to Average house prices", mae_percent)

    # Set a tag to identify the experiment run
    mlflow.set_tag("Training Info", "Baseline Model- Linear Regression Model")

    # Infer the model signature
    signature = infer_signature(X_test, model.predict(X_test))

    # Log the model
    model_info = mlflow.sklearn.log_model(
        sk_model= model,
        artifact_path="linear_reg_model",
        signature=signature,
        input_example=X_test,
        registered_model_name="linear_reg_model"
    )

    # Note down this model uri to retrieve the model in the future for scoring
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
lower_bound, upper_bound = bootstrap_prediction_interval(model, X_train, y_train, X_test)

# Add the predicted prices and the prediction interval bounds to the test DataFrame (before scaling)
X_test['Predicted Price'] = y_pred
X_test['Lower Bound'] = lower_bound
X_test['Upper Bound'] = upper_bound
