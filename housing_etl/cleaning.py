# housing_etl/cleaning.py
import pandas as pd
def clean_data(df):
    def is_price_per_sqft(val):
        return isinstance(val, str) and 'psf' in val

    def is_year(val):
        return isinstance(val, str) and val.isdigit() and len(val) == 4

    for idx, row in df.iterrows():
        if is_price_per_sqft(row['year']):
            df.at[idx, 'road_name'] = row['size_sqft']
            df.at[idx, 'size_sqft'] = row['price_per_sqft']
            df.at[idx, 'price_per_sqft'] = row['year']
            if is_year(row['area']):
                df.at[idx, 'year'] = row['area']
            else:
                df.at[idx, 'year'] = ""

    df = df[~df['year'].str.contains(r'[^0-9]', na=False)]
    df = df[df['year'] != '']
    df = df.dropna(subset=['size_sqft'])
    df = df[df['size_sqft'] != '']

    df['price'] = df['price'].replace(r'[^\d.]', '', regex=True).astype(float)
    df['price_per_sqft'] = df['price_per_sqft'].replace(r'[^\d.]', '', regex=True).astype(float)
    df['size_sqft'] = df['size_sqft'].replace(r'[^\d,]', '', regex=True).str.replace(',', '').astype(float)
    df['n_bedrooms'] = df['n_bedrooms'].str.extract(r'(\d+)').astype(int)
    df['n_bathrooms'] = df['n_bathrooms'].str.extract(r'(\d+)').astype(int)
    df['year'] = pd.to_numeric(df['year'], downcast="integer")
    df['scraped_date'] = pd.to_datetime(df['scraped_date'], errors='coerce')
    return df
