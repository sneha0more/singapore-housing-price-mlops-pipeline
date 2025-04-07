import shap
import pandas as pd
import lightgbm as lgb
import sqlalchemy
from sklearn.preprocessing import StandardScaler, LabelEncoder
import mlflow
import mlflow.lightgbm
import matplotlib.pyplot as plt
import os
import numpy as np

# Set MLflow tracking URI
mlflow.set_tracking_uri("http://127.0.0.1:5000")

# Step 1: Load trained LightGBM model from MLflow
print("Loading trained model from MLflow...")
model = mlflow.lightgbm.load_model('runs:/fa5dce4130b34620bbc76a731ee86502/lightgbm_model')
print("Model loaded successfully.")

# Step 2: Load data
print("Loading data from MySQL database...")
engine = sqlalchemy.create_engine("mysql+pymysql://root:root@localhost:3306/housing_db")
df = pd.read_sql("SELECT * FROM housing_data", engine)

# Step 3: Preprocess data (same as training)
print("Preprocessing data...")
df_subset = df.drop(columns=['id', 'block', 'street', 'scraped_date', 'scraped_month', 'scraped_year'])

df_subset = pd.get_dummies(df_subset, columns=['n_rooms', 'district', 'region', 'area', 'n_bedrooms', 'n_bathrooms'], drop_first=True, dtype=int)

label_encoder = LabelEncoder()
df_subset['is_central'] = label_encoder.fit_transform(df_subset['is_central'])
df_subset['is_mature_town'] = label_encoder.fit_transform(df_subset['is_mature_town'])

X = df_subset.drop('price', axis=1)

# Step 4: Manually define selected features
selected_features = [
    'lease_commence_date', 'remaining_lease', 'floor_area_sqm', 'storey_range', 'resale_price',
    'is_central', 'is_mature_town', 'n_rooms_3', 'n_rooms_4', 'district_3',
    'district_5', 'district_12', 'region_North', 'region_West', 'area_Tampines',
    'n_bedrooms_3', 'n_bedrooms_4', 'n_bathrooms_2', 'n_bathrooms_3', 'n_bathrooms_4'
]

print("Aligning dataset to selected features...")
for col in selected_features:
    if col not in X.columns:
        print(f"Adding missing column: {col}")
        X[col] = 0

X = X[selected_features]

# Step 5: Scale features
print("Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled, columns=selected_features)

# Step 6: SHAP Explainer
print("Initializing SHAP explainer...")
explainer = shap.TreeExplainer(model)
print("Calculating SHAP values...")
shap_values = explainer(X_scaled)

# Step 7: Visualize and Export SHAP Plots

# Create output directory
output_dir = "shap_outputs"
os.makedirs(output_dir, exist_ok=True)

# Summary plot
print("Generating SHAP summary plot...")
plt.figure()
shap.summary_plot(shap_values, X_scaled_df, show=False)
summary_plot_path = os.path.join(output_dir, "shap_summary_plot.png")
plt.tight_layout()
plt.savefig(summary_plot_path)
plt.close()
print(f"Saved: {summary_plot_path}")

# Bar plot
print("Generating SHAP bar plot...")
plt.figure()
shap.summary_plot(shap_values, X_scaled_df, plot_type="bar", show=False)
bar_plot_path = os.path.join(output_dir, "shap_bar_plot.png")
plt.tight_layout()
plt.savefig(bar_plot_path)
plt.close()
print(f"Saved: {bar_plot_path}")

# Dependence plot for top feature
print("Selecting top feature for dependence plot dynamically...")
shap_mean = np.abs(shap_values.values).mean(axis=0)
top_feature = selected_features[np.argmax(shap_mean)]
print(f"Top feature selected: {top_feature}")

print(f"Generating SHAP dependence plot for: {top_feature}")
plt.figure()
shap.dependence_plot(top_feature, shap_values.values, X_scaled_df, show=False)
dependence_plot_path = os.path.join(output_dir, f"shap_dependence_plot_{top_feature}.png")
plt.tight_layout()
plt.savefig(dependence_plot_path)
plt.close()
print(f"Saved: {dependence_plot_path}")

# Step 8: Log artifacts to MLflow
with mlflow.start_run(run_name="SHAP Explainability", nested=True):
    mlflow.log_artifact(summary_plot_path)
    mlflow.log_artifact(bar_plot_path)
    mlflow.log_artifact(dependence_plot_path)
    print("SHAP visualizations logged to MLflow.")

print("SHAP explainability completed successfully and artifacts logged.")
