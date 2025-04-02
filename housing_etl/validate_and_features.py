# housing_etl/features.py
import pandas as pd

def validate_and_engineer_features(df):
    df = df.dropna(subset=['year'])
    df = df.drop_duplicates()
    df = df[(df['n_bedrooms'] > 0) & (df['n_bathrooms'] > 0)]
    df['scraped_date'] = pd.to_datetime(df['scraped_date'], errors='coerce')
    df = df.rename(columns={'year': 'build_year'})

    df['flat_age'] = 2025 - df['build_year']
    df['lease_remaining'] = 99 - df['flat_age']
    df['price_per_bedroom'] = df['price'] / df['n_bedrooms']
    df['size_per_room'] = df['size_sqft'] / df['n_bedrooms']
    df['bed_bath_ratio'] = df['n_bedrooms'] / df['n_bathrooms']
    df['scraped_month'] = df['scraped_date'].dt.month
    df['scraped_year'] = df['scraped_date'].dt.year
    df['is_central'] = (df['region'].str.lower() == 'central').astype(int)

    mature_towns = ['Ang Mo Kio', 'Bedok', 'Bishan', 'Bukit Merah', 'Bukit Timah', 'Central Area',
                    'Clementi', 'Geylang', 'Kallang/Whampoa', 'Marine Parade', 'Pasir Ris', 'Queenstown',
                    'Serangoon', 'Tampines', 'Toa Payoh']
    df['is_mature_town'] = df['area'].isin(mature_towns).astype(int)
    df['age_size_interaction'] = df['flat_age'] * df['size_sqft']
    df['lease_price_interaction'] = df['lease_remaining'] * df['price_per_sqft']
    df['block'] = df['title'].str.extract(r'^(\d+\w?)')
    df = df.rename(columns={'road_name': 'street'})
    df = df.drop(columns=[col for col in ['title', 'Unnamed: 0', 'Unnamed: 0.1'] if col in df.columns])
    return df