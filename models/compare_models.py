import pandas as pd
import numpy as np
from operator import itemgetter
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import RFE
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score
import sqlalchemy
import mlflow

# Collecting data from database housing_db
engine = sqlalchemy.create_engine("mysql+pymysql://root:root@localhost:3306/housing_db")
df = pd.read_sql("SELECT * FROM housing_data", engine)
df_subset = df.drop(columns=['id', 'block', 'street', 'scraped_date', 'scraped_month', 'scraped_year'])

X = df_subset.drop('price', axis=1)
Y = df_subset['price']


def get_test_subset(X, Y):
    estimator = LinearRegression()
    X_number = X.select_dtypes(include=['number']).copy()
    selector = RFE(estimator, n_features_to_select=20)
    selector.fit(X_number, Y)

    # Get the selected features from RFE
    selected_features = X_number.columns[selector.support_]
    # Train-test split features
    X_selected = X_number[selected_features]
    X_train, X_test, y_train, y_test = train_test_split(X_selected, Y, test_size=0.30, random_state=42)
    return X_test, y_test


def evaluate(y_test, y_pred):
    rmse = root_mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    average_price = np.mean(y_test)
    # To calculate relative error:
    mae_percent = (mae / average_price) * 100
    rmse_percent = (rmse / average_price) * 100
    return mae, rmse, r2, mae_percent, rmse_percent

model_uris = ['runs:/aa35d823471a4d57b1fccc3a36c2d3d8/linear_reg_model']
mlflow.set_tracking_uri(uri="http://localhost:5000")

def main():
    # parser = argparse.ArgumentParser(description="Compare multiple MLflow-logged models using the same test set.")
    # parser.add_argument("--model_uris", nargs="+", required=True, help="List of MLflow model URIs")
    # parser.add_argument("--X_test_path", type=str, required=True, help="Path to X_test CSV file")
    # parser.add_argument("--y_test_path", type=str, required=True, help="Path to y_test CSV file")
    # args = parser.parse_args()

    print("Loading test data...")
    X_test, y_test = get_test_subset(X, Y)

    results = []

    for uri in model_uris:
        print(f"\n Loading model from: {uri}")
        try:
            model = mlflow.pyfunc.load_model(uri)
            preds = model.predict(X_test)
            mae, rmse, r2, mae_percent, rmse_percent = evaluate(y_test, preds)
            results.append({
                "model_uri": uri,
                "mae": mae,
                "rmse": rmse,
                "r2": r2,
                "mae_percent": mae_percent,
                "rmse_percent": rmse_percent
            })
        except Exception as e:
            print(f"Failed to evaluate model {uri}: {e}")

    print("\nComparison Results:")
    df_results = pd.DataFrame(results)
    print(df_results.to_string(index=False))

    df_results.to_csv("models/model_comparison_results.csv", index=False)
    print("\nSaved results to model_comparison_results.csv")


if __name__ == "__main__":
    main()

#
# runs:/4633694a7ba04ba588d4b914869b46f8/xgboost_model
# runs:/1d9bef0f160b4d6583fc0b17138bbc09/lightgbm_model
# runs:/bb4d4d5618b94532b6e74f49a5ec436b/random_forest_model