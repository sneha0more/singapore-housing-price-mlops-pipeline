import pandas as pd
import os
from sqlalchemy import create_engine

# MySQL database connection configuration
engine = create_engine("mysql+pymysql://root:root@mysql_housing_v2/housing_db")


# Load cleaned CSV
csv_path = os.path.join(os.path.dirname(__file__), "enhanced_data.csv")
df = pd.read_csv(csv_path)


# Ensure scraped_date is parsed as date
df["scraped_date"] = pd.to_datetime(df["scraped_date"], errors="coerce")

# Load into MySQL
df.to_sql("housing_data", con=engine, if_exists="append", index=False)

print("Data loaded successfully!")





# Load cleaned CSV -- User Input data
user_input_csv_path = os.path.join(os.path.dirname(__file__), "user_input_data.csv")
df = pd.read_csv(user_input_csv_path)

# Load into MySQL
df.to_sql("input_data", con=engine, if_exists="append", index=False)

print("User Input Data loaded successfully!")