# from preprocessing import preprocess_user_input 
# from predictor import predict_price

import streamlit as st
import requests

st.set_page_config(page_title="Housing Price Prediction", page_icon="🏡")

# Title
st.markdown("## **Housing Price Prediction Model 🏡**")
st.markdown(
    "This model outputs a recommended listing price for sellers "
    "based on the characteristics of their HDB flat."
)

st.markdown("### Input Flat Characteristics")

# Example dropdown values
hdb_types = [
    "HDB 3-Room",
    "HDB 5-Room",
    "HDB 4-Room",
    "HDB 4PA (Premium Apartment)",
    "HDB 3PA (Premium Apartment)",
    "HDB 5PA (Premium Apartment)",
    "HDB Exec Apartment",
    "HDB 2-Room",
    "HDB Exec Maisonette"
]

areas = [
    "Bukit Merah",
    "Queenstown",
    "Clementi",
    "Kallang/Whampoa",
    "Bukit Timah",
    "Toa Payoh",
    "Geylang",
    "Bedok",
    "Marine Parade",
    "Pasir Ris",
    "Tampines",
    "Hougang",
    "Sengkang",
    "Punggol",
    "Serangoon",
    "Bishan",
    "Ang Mo Kio",
    "Jurong West",
    "Jurong East",
    "Bukit Panjang",
    "Bukit Batok",
    "Choa Chu Kang",
    "Woodlands",
    "Sembawang",
    "Yishun"
]


districts = [
    "Raffles Place, Cecil, Marina, People's Park",
    "Anson, Tanjong Pagar",
    "Queenstown, Tiong Bahru",
    "Telok Blangah, Harbourfront",
    "Pasir Panjang, Hong Leong Garden, Clementi New Town",
    "Middle Road, Golden Mile",
    "Little India",
    "Ardmore, Bukit Timah, Holland Road, Tanglin",
    "Watten Estate, Novena, Thomson",
    "Balestier, Toa Payoh, Serangoon",
    "Macpherson, Braddell",
    "Geylang, Eunos",
    "Katong, Joo Chiat, Amber Road",
    "Bedok, Upper East Coast, Eastwood, Kew Drive",
    "Loyang, Changi",
    "Tampines, Pasir Ris",
    "Serangoon Garden, Hougang, Ponggol",
    "Bishan, Ang Mo Kio",
    "Upper Bukit Timah, Clementi Park, Ulu Pandan",
    "Jurong",
    "Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang",
    "Kranji, Woodgrove",
    "Yishun, Sembawang",
    "Seletar"
]

bedroom_options = [1, 2, 3, 4, 5, 6]
bathroom_options = [1, 2, 3, 4]

# Layout in two columns
col1, col2 = st.columns(2)

with col1:
    hdb_type = st.selectbox("HDB type", hdb_types)
    area = st.selectbox("Area", areas)
    size_sqft = st.text_input("Size (in sqft)")

with col2:
    district = st.selectbox("District", districts)
    build_year = st.text_input("Build Year")
    
col3, col4 = st.columns(2)
with col3:
    n_bedrooms = st.selectbox("Number of bedrooms", bedroom_options)
with col4:
    n_bathrooms = st.selectbox("Number of bathrooms", bathroom_options)

# Button
run_model = st.button("Run Model")

# Result display (placeholder output)
if run_model:
    region_map = {
        "Bukit Merah": "Central", "Queenstown": "Central", "Kallang/Whampoa": "Central", "Toa Payoh": "Central",
        "Bedok": "East", "Marine Parade": "East", "Pasir Ris": "East", "Tampines": "East",
        "Hougang": "North-East", "Sengkang": "North-East", "Punggol": "North-East", "Serangoon": "North-East",
        "Bishan": "North", "Ang Mo Kio": "North", "Yishun": "North", "Woodlands": "North", "Sembawang": "North",
        "Clementi": "West", "Jurong West": "West", "Jurong East": "West", "Bukit Panjang": "West", "Bukit Batok": "West", "Choa Chu Kang": "West"
    }
    inferred_region = region_map.get(area, "Unknown")

    input_dict = {
        'build_year': int(build_year),
        'size_sqft': float(size_sqft),
        'n_bedrooms': int(n_bedrooms),
        'n_bathrooms': int(n_bathrooms),
        'area': area,
        'district': district,
        'region': inferred_region,  # You can derive this with a helper
        'n_rooms': hdb_type
    }

# Predict using the model
    try:
        response = requests.post("http://localhost:8000/predict", json=input_dict)
        if response.status_code == 200:
            r = response.json()
            prediction = r["predicted_price"]
            st.success(f"💰 Estimated Price: ${prediction:,.2f}")
            
            # Calculate ±5% range
            lower = r["price_range"]["lower"]
            upper = r["price_range"]["upper"]

            # Styled property listing output
            st.markdown("### 💰 Recommended Listing Price Range")
            st.markdown(
                f"<div style='font-size:32px; font-weight:bold; color:#ff7e00;'>"
                f"${lower:,.0f} – ${upper:,.0f} SGD"
                f"</div>",
                unsafe_allow_html=True
            )

            # Optional subtitle
            st.markdown(
                "<span style='font-size:14px; color:gray;'>Estimated based on similar listings and resale trends</span>",
                unsafe_allow_html=True
            )

    except Exception as e:
        st.error(f"Prediction failed: {e}")
        print("❌ Frontend exception:", e) 
        st.markdown("### Recommended Listing Price")
        st.markdown("## **<span style='color:orange'>895,239 - 930,020</span>**", unsafe_allow_html=True)