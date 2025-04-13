import streamlit as st
import requests

st.set_page_config(page_title="Housing Price Prediction", page_icon="🏡")

st.markdown("## **Housing Price Prediction Model 🏡**")
st.markdown(
    "This model outputs a recommended listing price for sellers based on the characteristics of their HDB flat based on recent listing data on Edgeprop."
)
st.markdown("### Input Flat Characteristics")

# Dropdown options
hdb_types = [
    "HDB 3-Room", "HDB 5-Room", "HDB 4-Room", "HDB 4PA (Premium Apartment)",
    "HDB 3PA (Premium Apartment)", "HDB 5PA (Premium Apartment)",
    "HDB Exec Apartment", "HDB 2-Room", "HDB Exec Maisonette"
]

areas = [
    "Bukit Merah", "Queenstown", "Clementi", "Kallang/Whampoa", "Bukit Timah",
    "Toa Payoh", "Geylang", "Bedok", "Marine Parade", "Pasir Ris", "Tampines",
    "Hougang", "Sengkang", "Punggol", "Serangoon", "Bishan", "Ang Mo Kio",
    "Jurong West", "Jurong East", "Bukit Panjang", "Bukit Batok", "Choa Chu Kang",
    "Woodlands", "Sembawang", "Yishun"
]

districts = [
    "Raffles Place, Cecil, Marina, People's Park", "Anson, Tanjong Pagar",
    "Queenstown, Tiong Bahru", "Telok Blangah, Harbourfront",
    "Pasir Panjang, Hong Leong Garden, Clementi New Town",
    "Middle Road, Golden Mile", "Little India",
    "Ardmore, Bukit Timah, Holland Road, Tanglin",
    "Watten Estate, Novena, Thomson", "Balestier, Toa Payoh, Serangoon",
    "Macpherson, Braddell", "Geylang, Eunos", "Katong, Joo Chiat, Amber Road",
    "Bedok, Upper East Coast, Eastwood, Kew Drive", "Loyang, Changi",
    "Tampines, Pasir Ris", "Serangoon Garden, Hougang, Ponggol",
    "Bishan, Ang Mo Kio", "Upper Bukit Timah, Clementi Park, Ulu Pandan",
    "Jurong", "Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang",
    "Kranji, Woodgrove", "Yishun, Sembawang", "Seletar"
]

# Mapping to validate area-district consistency
area_district_map = {
    "Bukit Merah": ["Queenstown, Tiong Bahru", "Telok Blangah, Harbourfront"],
    "Queenstown": ["Queenstown, Tiong Bahru"],
    "Clementi": ["Pasir Panjang, Hong Leong Garden, Clementi New Town"],
    "Kallang/Whampoa": ["Middle Road, Golden Mile"],
    "Bukit Timah": ["Ardmore, Bukit Timah, Holland Road, Tanglin"],
    "Toa Payoh": ["Balestier, Toa Payoh, Serangoon"],
    "Geylang": ["Geylang, Eunos"],
    "Bedok": ["Bedok, Upper East Coast, Eastwood, Kew Drive"],
    "Marine Parade": ["Katong, Joo Chiat, Amber Road"],
    "Pasir Ris": ["Tampines, Pasir Ris"],
    "Tampines": ["Tampines, Pasir Ris"],
    "Hougang": ["Serangoon Garden, Hougang, Ponggol"],
    "Sengkang": ["Serangoon Garden, Hougang, Ponggol"],
    "Punggol": ["Serangoon Garden, Hougang, Ponggol"],
    "Serangoon": ["Balestier, Toa Payoh, Serangoon"],
    "Bishan": ["Bishan, Ang Mo Kio"],
    "Ang Mo Kio": ["Bishan, Ang Mo Kio"],
    "Jurong West": ["Jurong"],
    "Jurong East": ["Jurong"],
    "Bukit Panjang": ["Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang"],
    "Bukit Batok": ["Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang"],
    "Choa Chu Kang": ["Hillview, Dairy Farm, Bukit Panjang, Choa Chu Kang"],
    "Woodlands": ["Kranji, Woodgrove"],
    "Sembawang": ["Yishun, Sembawang"],
    "Yishun": ["Yishun, Sembawang"]
}

bedroom_options = [1, 2, 3, 4, 5, 6]
bathroom_options = [1, 2, 3, 4]

# Layout
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

run_model = st.button("Run Model")

if run_model:
    error_msgs = []

    # Validation logic
    if not size_sqft.strip() or not build_year.strip():
        error_msgs.append("Please fill in all the required fields.")

    try:
        size_val = float(size_sqft)
        if size_val <= 0:
            error_msgs.append("Size must be a positive number.")
    except:
        error_msgs.append("Size must be a numeric value.")

    if not build_year.isdigit() or not (1930 <= int(build_year) <= 2025):
        error_msgs.append("Build year must be a valid 4-digit number after 1930.")

    # Check area-district pair
    valid_districts = area_district_map.get(area, [])
    if district not in valid_districts:
        error_msgs.append(f"Selected district is not commonly associated with {area}.")

    if error_msgs:
        for err in error_msgs:
            st.error(err)
    else:
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
            'region': inferred_region,
            'n_rooms': hdb_type
        }

        try:
            response = requests.post("http://localhost:8000/predict", json=input_dict)
            if response.status_code == 200:
                r = response.json()
                prediction = r["predicted_price"]
                st.success(f"💰 Estimated Price: ${prediction:,.2f}")

                lower = r["price_range"]["lower"]
                upper = r["price_range"]["upper"]

                st.markdown("### 💰 Recommended Listing Price Range")
                st.markdown(
                    f"<div style='font-size:32px; font-weight:bold; color:#ff7e00;'>"
                    f"${lower:,.0f} – ${upper:,.0f} SGD"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    "<span style='font-size:14px; color:gray;'>Estimated based on similar listings and resale trends</span>",
                    unsafe_allow_html=True
                )
            else:
                st.error("Prediction request failed. Please try again.")
        except Exception as e:
            st.error(f"Prediction failed: {e}")
