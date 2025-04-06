import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
import numpy as np
import pandas as pd 
from operator import itemgetter
import sqlalchemy
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFE
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score

# Collecting data from database housing_db
engine = sqlalchemy.create_engine("mysql+pymysql://root:root@localhost:3306/housing_db")
df = pd.read_sql("SELECT * FROM housing_data", engine)

X = df[df.columns[1:]]
Y = df['price']

# -------------- Feature Selection -------------------
# calculate the correlation matrix between the features and the target variable:
corr_matrix = df.corr()
corr_with_target = corr_matrix['price']
#sort the correlation values in descending order and select the top k features:
k = 13
top_k = corr_with_target.sort_values(ascending=False)[:k].index
selected_features = df[top_k]
#check the correlation matrix between the selected features:
selected_corr_matrix = selected_features.corr()
X_selected_corr = selected_features.columns[1:] #exclude 'price' column 

# feature selection using RFE
estimator = LinearRegression()
X_number = X.select_dtypes(include=['number']).copy()
selector = RFE(estimator, n_features_to_select=12)
selector.fit(X_number, Y)

features = X_number.columns.to_list()
X_selected_rfe = []
for x, y in (sorted(zip(selector.ranking_ , features), key=itemgetter(0))):
    X_selected_rfe.append(str(y))

# Select features that are in both correlation method and RFE method 
features_selected = set(X_selected_corr).intersection(set(X_selected_rfe)) 


# Train-test split features
X_selected = df[features_selected]
X_train, X_test, y_train, y_test = train_test_split(X_selected, Y, test_size=0.30, random_state=42)

mlflow.set_tracking_uri(uri = "http://localhost:5000")  # Replace with host machine IP
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
    # mlflow.sklearn.log_model(model, "model")

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