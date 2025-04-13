import pandas as pd
from api.predictor import predict_price
from api.preprocessing import preprocess_user_input  # Make sure to import your preprocessing function

def test_predict_price_valid_input():
    # Prepare the input dictionary with necessary columns for preprocessing
    input_dict = {
        "build_year": 2010,
        "size_sqft": 1200.0,
        "n_bedrooms": 3,
        "n_bathrooms": 2,
        "area": "Orchard",
        "district": "Ardmore, Bukit Timah, Holland Road, Tanglin",
        "region": "Central Region",
        "n_rooms": "HDB 4-Room"
    }
    
    # Preprocess the input using the function
    preprocessed_data = preprocess_user_input(input_dict)
    
    # Convert the preprocessed data into a DataFrame if necessary
    #df = pd.DataFrame([preprocessed_data])
    
    # Use the preprocessed data to predict the price
    result = predict_price(preprocessed_data)
    
    # Assertions
    assert isinstance(result, float)
    assert result > 0
