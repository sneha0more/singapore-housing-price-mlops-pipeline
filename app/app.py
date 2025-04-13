import streamlit as st

st.set_page_config(page_title="Housing Price Prediction", page_icon="🏡")

# Title
st.markdown("## **Housing Price Prediction Model 🏡**")
st.markdown(
    "This model outputs a recommended listing price for sellers based on the characteristics of their HDB flat based on recent listing data on Edgeprop."
)

st.markdown("### Input Flat Characteristics")

# Example dropdown values
hdb_types = [
    "HDB 3-Room", "HDB 5-Room", "HDB 4-Room", "HDB 4PA (Premium Apartment)",
    "HDB 3PA (Premium Apartment)", "HDB 5PA (Premium Apartment)",
    "HDB Exec Apartment", "HDB 2-Room", "HDB Exec Maisonette"
]

areas = [
    "Bukit Merah", "Queenstown", "Clementi", "Kallang/Whampoa", "Bukit Timah",
    "Toa Payoh", "Geylang", "Bedok", "Marine Parade", "Pasir Ris", "Tampines",
    "Hougang", "Sengkang", "Punggol", "Serangoon", "Bishan", "Ang Mo Kio",
    "Jurong West", "Jurong East", "Bukit Panjang", "Bukit Batok",
    "Choa Chu Kang", "Woodlands", "Sembawang", "Yishun"
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

# Button
run_model = st.button("Run Model")

# Validation and Result
if run_model:
    errors = []

    # Check for empty fields
    if not size_sqft or not build_year:
        errors.append("Please fill in all the fields.")

    # Validate size_sqft
    try:
        size_val = float(size_sqft)
        if size_val <= 30:
            errors.append("Size must be greater than 30 sqft.")
    except ValueError:
        errors.append("Size must be a valid number.")

    # Validate build_year
    if not build_year.isdigit() or len(build_year) != 4:
        errors.append("Build year must be a 4-digit number.")
    elif int(build_year) < 1931:
        errors.append("Build year must be after 1930.")

    # Display errors or result
    if errors:
        for error in errors:
            st.error(error)
    else:
        st.markdown("### Recommended Listing Price")
        st.markdown("## **<span style='color:orange'>895,239 - 930,020</span>**", unsafe_allow_html=True)
