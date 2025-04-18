from sqlalchemy import create_engine
import pandas as pd

TARGET_DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "housing_db",
    # "port": 3306  # optional, default is 3306
    "port": 3307
}

def load_to_db(df):
    """
    Loads data into MySQL only if a row with the exact same column values doesn't already exist.
    """
    engine = create_engine(
        f"mysql+pymysql://{TARGET_DB_CONFIG['user']}:{TARGET_DB_CONFIG['password']}@"
        f"{TARGET_DB_CONFIG['host']}/{TARGET_DB_CONFIG['database']}"
    )

    table_name = "housing_data"

    if engine.has_table(table_name):
        # Load existing table
        existing = pd.read_sql(f"SELECT * FROM {table_name}", con=engine)

        # Align columns to ensure exact match
        common_cols = df.columns.intersection(existing.columns).tolist()
        df_subset = df[common_cols]
        existing_subset = existing[common_cols]

        # Concatenate and drop duplicates to find new rows
        combined = pd.concat([existing_subset, df_subset])
        deduped = combined.drop_duplicates(keep=False)

        # Keep only rows that exist in df but not in existing
        df_final = df_subset.merge(deduped, how='inner', on=common_cols)
    else:
        df_final = df.copy()

    # Load only new rows
    if not df_final.empty:
        df_final.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"✅ {len(df_final)} new unique rows loaded into `{table_name}`.")
    else:
        print("⚠️ No new unique rows to load.")
