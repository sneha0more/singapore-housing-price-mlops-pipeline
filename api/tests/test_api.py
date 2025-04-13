from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)

def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "🏡 Housing Price Prediction API is live!"}

def test_predict_endpoint_valid():
    response = client.post("/predict", json={
        "build_year": 2010,
        "size_sqft": 1200.0,
        "n_bedrooms": 3,
        "n_bathrooms": 2,
        "area": "Orchard",
        "district": "Ardmore, Bukit Timah, Holland Road, Tanglin",
        "region": "Central Region",
        "n_rooms": "HDB 4-Room"
    })
    assert response.status_code == 200
    result = response.json()
    assert "predicted_price" in result
    assert "price_range" in result

def test_predict_endpoint_invalid_input():
    # Missing fields
    response = client.post("/predict", json={
        "build_year": 2010,
        "size_sqft": 1200.0
    })
    assert response.status_code == 422  # Unprocessable Entity (validation error)
