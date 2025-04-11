import pandas as pd
from drift_detetction import generate_drift_report 

incoming_df = pd.read_csv("../data/enhanced_data1.csv")
output_path = "../data/test_drift_report.csv"

# Run the drift detection function
generate_drift_report(incoming_df, output_path)