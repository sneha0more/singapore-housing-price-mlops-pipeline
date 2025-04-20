import pandas as pd
import scipy.stats as stats
import numpy as np
import os
from sqlalchemy import create_engine
from sqlalchemy import text

TARGET_DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "housing_db",
}

def generate_drift_report(incoming_df, output_path):
    """
    Compares the reference dataset and the new dataset using:
    - KS-test for numeric columns
    - Chi-square test for categorical columns
    Outputs drift_report.csv with test statistics and p-values.
    """
    drift_results = []

    # Create engine to connect to MySQL
    engine = create_engine(
        f"mysql+pymysql://{TARGET_DB_CONFIG['user']}:{TARGET_DB_CONFIG['password']}@"
        f"{TARGET_DB_CONFIG['host']}/{TARGET_DB_CONFIG['database']}"
    )


    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM housing_data"))
        columns = result.keys()  # This gives you column names
        rows = result.fetchall()  # This gives you the actual data
        # Convert to DataFrame
        reference_df = pd.DataFrame(rows, columns=columns)
        print(reference_df.head)

        common_cols = [col for col in reference_df.columns if col in incoming_df.columns]
        reference_df = reference_df[common_cols].copy()
        incoming_df = incoming_df[common_cols].copy()

        for col in common_cols:
            if pd.api.types.is_numeric_dtype(reference_df[col]):
                # Use KS-test for numerical columns
                stat, p_value = stats.ks_2samp(reference_df[col].dropna(), incoming_df[col].dropna())
                test_type = "KS-test"
            else:
                # Use Chi-square for categorical columns
                ref_counts = reference_df[col].value_counts()
                new_counts = incoming_df[col].value_counts()
                combined_df = pd.concat([ref_counts, new_counts], axis=1, sort=False).fillna(0)
                combined_df.columns = ['ref', 'new']

                # Adjust expected frequencies to match observed total
                f_obs = combined_df['ref']
                f_exp_raw = combined_df['new']
                if f_exp_raw.sum() == 0:
                    f_exp_raw += 1e-8
                f_exp = f_exp_raw * (f_obs.sum() / f_exp_raw.sum())

                # Avoid zero in expected
                f_exp = f_exp.replace(0, 1e-8)

                chi2_stat, p_value = stats.chisquare(f_obs, f_exp=f_exp)
                stat = chi2_stat
                test_type = "Chi-square"

            drift_results.append({
                "column": col,
                "test": test_type,
                "statistic": round(stat, 4),
                "p_value": round(p_value, 4),
                "drift_detected": p_value < 0.05
            })

        drift_df = pd.DataFrame(drift_results)

        # Ensure output directory exists
        drift_df.to_csv(output_path, index=False)
        print(f"✅ Drift report saved to {output_path}")
 
    
