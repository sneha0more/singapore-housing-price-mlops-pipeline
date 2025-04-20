print("✅ FastAPI app is starting...")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import traceback
import pandas as pd

from predictor import predict_price
from preprocessing import preprocess_user_input
import mysql.connector
from mysql.connector import Error
import os
import csv
from datetime import datetime



app = FastAPI()


def save_input_to_mysql(df_input):
    try:
        TARGET_DB_CONFIG = {
            "host": "localhost",
            "user": "root",
            "password": "root",
            "database": "housing_db", 
            "port": 3307  # Specify the port if it's different from the default
        }

        conn = mysql.connector.connect(**TARGET_DB_CONFIG)
        cur = conn.cursor()
        datetime_now = datetime.now()

        # Extract row data from DataFrame (first row)
        row = df_input.iloc[0]
        # Insert the row into the 'property_data' table
        cur.execute('''
            INSERT INTO input_data (
                build_year, size_sqft, size_per_room, bed_bath_ratio, is_central, is_mature_town,
                age_size_interaction, n_rooms_HDB_4_Room, n_rooms_HDB_5PA_Premium_Apartment,
                district_Balestier_Toa_Payoh_Serangoon, district_Geylang_Eunos,
                district_Hillview_Dairy_Farm_Bukit_Panjang_Choa_Chu_Kang, district_Jurong,
                district_Queenstown_Tiong_Bahru, district_Telok_Blangah_Harbourfront,
                region_East, region_North, region_West, area_Hougang, area_Marine_Parade, input_datetime
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            row['build_year'], row['size_sqft'], row['size_per_room'], row['bed_bath_ratio'],
            row['is_central'], row['is_mature_town'], row['age_size_interaction'],
            row['n_rooms_HDB 4-Room'], row['n_rooms_HDB 5PA (Premium Apartment)'],
            row['district_Balestier, Toa Payoh, Serangoon'], row['district_Geylang, Eunos'],
            row['district_Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang'], row['district_Jurong'],
            row['district_Queenstown, Tiong Bahru'], row['district_Telok Blangah, Harbourfront'],
            row['region_East'], row['region_North'], row['region_West'],
            row['area_Hougang'], row['area_Marine Parade'], datetime_now
        ))

        
        conn.commit()



        # Write the data to a CSV file
        # Get root directory path relative to current file
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        csv_filename = os.path.join(root_dir, 'housing_loader_package', 'user_input_data.csv')
       
        
        # Check if the file is empty, and if it doesn't, write the header
        file_exists = os.path.isfile(csv_filename) and os.path.getsize(csv_filename) > 0


        
        # Write data to CSV (append if file already exists, otherwise write a new file)
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write header if the file is new
            if not file_exists:
                writer.writerow([
                    'build_year', 'size_sqft', 'size_per_room', 'bed_bath_ratio', 'is_central', 
                    'is_mature_town', 'age_size_interaction', 'n_rooms_HDB_4_Room', 
                    'n_rooms_HDB_5PA_Premium_Apartment', 'district_Balestier_Toa_Payoh_Serangoon', 
                    'district_Geylang_Eunos', 'district_Hillview_Dairy_Farm_Bukit_Panjang_Choa_Chu_Kang', 
                    'district_Jurong', 'district_Queenstown_Tiong_Bahru', 
                    'district_Telok_Blangah_Harbourfront', 'region_East', 'region_North', 
                    'region_West', 'area_Hougang', 'area_Marine_Parade', 'input_datetime'
                ])
            # Write the row data to the CSV
            writer.writerow([
                row['build_year'], row['size_sqft'], row['size_per_room'], row['bed_bath_ratio'],
                row['is_central'], row['is_mature_town'], row['age_size_interaction'],
                row['n_rooms_HDB 4-Room'], row['n_rooms_HDB 5PA (Premium Apartment)'],
                row['district_Balestier, Toa Payoh, Serangoon'], row['district_Geylang, Eunos'],
                row['district_Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang'], row['district_Jurong'],
                row['district_Queenstown, Tiong Bahru'], row['district_Telok Blangah, Harbourfront'],
                row['region_East'], row['region_North'], row['region_West'],
                row['area_Hougang'], row['area_Marine Parade'], datetime_now
            ])
        


        cur.close()
        conn.close()
        print("Input data inserted into database!")



    except Error as e:
        print(f"❌ Error while inserting to MySQL: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn and conn.is_connected():
            conn.close()





@app.get("/")
def home():
    return {"message": "🏡 Housing Price Prediction API is live!"}

class InputData(BaseModel):
    build_year: int
    size_sqft: float
    n_bedrooms: int
    n_bathrooms: int
    area: str
    district: str
    region: str
    n_rooms: str

@app.post("/predict")
def predict(data: InputData):
    try:
        # Import inside the function to avoid crashing app during startup


        input_dict = data.dict()
        df_input = preprocess_user_input(input_dict)
        prediction = predict_price(df_input)
        save_input_to_mysql(df_input)

        print(df_input.columns)

        return {
            "predicted_price": round(prediction, 2),
            "price_range": {
                "lower": round(prediction * 0.95, 2),
                "upper": round(prediction * 1.05, 2)
            }
        }
    except Exception as e:
        print("❌ Backend exception:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
