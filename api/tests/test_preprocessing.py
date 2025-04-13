import pytest
from api.preprocessing import preprocess_user_input


def test_preprocess_valid_input():
    input_data = {
        "build_year": 2010,
        "size_sqft": 1200.0,
        "n_bedrooms": 3,
        "n_bathrooms": 2,
        "area": "Orchard",
        "district": "D09",
        "region": "Ardmore, Bukit Timah, Holland Road, Tanglin",
        "n_rooms": "HDB 4-Room"
    }
    df = preprocess_user_input(input_data)
    assert df is not None
    assert "size_sqft" in df.columns

def test_preprocess_missing_field():
    input_data = {
        "build_year": 2010,
        "size_sqft": 1200.0,
        # n_bedrooms is missing
        "n_bathrooms": 2,
        "area": "Orchard",
        "district": "D09",
        "region": "Central Region",
        "n_rooms": "3-4"
    }
    with pytest.raises(KeyError):
        preprocess_user_input(input_data)
