import pandas as pd
import os
from sqlalchemy import create_engine

# MySQL database connection configuration
engine = create_engine("mysql+pymysql://root:root@localhost:3306/housing_db")

# Load cleaned CSV
csv_path = os.path.join(os.path.dirname(__file__), "enhanced_data.csv")
df = pd.read_csv(csv_path)


# Ensure scraped_date is parsed as date
df["scraped_date"] = pd.to_datetime(df["scraped_date"], errors="coerce")

# Load into MySQL
df.to_sql("housing_data", con=engine, if_exists="append", index=False)

print("Data loaded successfully!")
