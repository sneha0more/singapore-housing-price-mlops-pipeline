import pandas as pd
import joblib

def preprocess_user_input(input_dict):
    df = pd.DataFrame([input_dict])

    df['build_year'] = df['build_year'].astype(int)
    df['size_sqft'] = df['size_sqft'].astype(float)
    df['n_bedrooms'] = df['n_bedrooms'].astype(int)
    df['n_bathrooms'] = df['n_bathrooms'].astype(int)

    df['size_per_room'] = df['size_sqft'] / df['n_bedrooms'].replace(0, 1)
    df['bed_bath_ratio'] = df['n_bedrooms'] / df['n_bathrooms'].replace(0, 1)
    df['is_central'] = 1 if input_dict['area'] in [
        'Bukit Merah', 'Queenstown', 'Toa Payoh', 'Kallang/Whampoa'
    ] else 0
    df['is_mature_town'] = 1 if input_dict['area'] in [
        'Ang Mo Kio', 'Bedok', 'Bishan', 'Bukit Merah', 'Bukit Timah', 'Central Area',
        'Clementi', 'Geylang', 'Kallang/Whampoa', 'Marine Parade', 'Pasir Ris',
        'Queenstown', 'Serangoon', 'Toa Payoh'
    ] else 0
    df['age_size_interaction'] = (2025 - df['build_year']) * df['size_sqft']

    one_hot_cols = {
        'n_rooms': ['HDB 4-Room', 'HDB 5PA (Premium Apartment)'],
        'district': [
            'Balestier, Toa Payoh, Serangoon',
            'Geylang, Eunos',
            'Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang',
            'Jurong',
            'Queenstown, Tiong Bahru',
            'Telok Blangah, Harbourfront'
        ],
        'region': ['East', 'North', 'West'],
        'area': ['Hougang', 'Marine Parade']
    }

    for col, values in one_hot_cols.items():
        for val in values:
            df[f"{col}_{val}"] = 1 if input_dict[col] == val else 0

   # ✅ Load expected feature list from model training
    selected_features = joblib.load("/app/models/models_dump_for_Registry/selected_features.joblib")

    # Fill in any missing columns
    for col in selected_features:
        if col not in df.columns:
            df[col] = 0

# Reorder columns to match training
    df = df[selected_features]

    return df
