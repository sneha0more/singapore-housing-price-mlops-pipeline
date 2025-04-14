# Housing Price Prediction Web App Frontend Backend Integration

This project is a full-stack machine learning application for recommending optimal listing prices for HDB flats in Singapore. It features a **Streamlit frontend** integrated with a **FastAPI backend** that serves a LightGBM model tracked and staged via **MLflow**. The model is trained on recent property listings data scraped from EdgeProp.

---

## 🌍 Project Overview

- **Frontend**: Streamlit UI for users (home sellers) to enter flat details and view price recommendations.
- **Backend**: FastAPI web service deployed in Docker that handles preprocessing, model inference, and returns price ranges.
- **Model**: LightGBM regressor with handcrafted features, feature selection, and scaling.
- **Model Registry**: MLflow used for version control and model staging.

---

## 🚀 How to Run Locally

### 1. Start MLflow UI (for model tracking)
Make sure you're inside your virtual environment and MLflow is installed.
```bash
source ~/python3venv/bin/activate
mlflow ui --host 0.0.0.0 --port 5000
```

> ⚠️ **Troubleshooting Tip**: If MLflow UI fails to start due to "address already in use", run `sudo lsof -i :5000` to identify the process and kill it using `sudo kill <PID>`.

---

### 2. Prepare Your Model Artifacts
Ensure the following files are placed inside the container at:
```
/app/models/models_dump_for_Registry/
├── scaler.joblib
├── selected_features.joblib
```
These are required for transforming the input data and selecting the model's trained features.

Ensure your model is registered and promoted to `Staging` in the MLflow Model Registry.

> 📍 The container expects MLflow server to be reachable at `http://172.17.0.1:5000`. This is the Docker host bridge IP.

---

### 3. Build and Run the Docker Container
```bash
# From the project root
sudo docker build -t housing-api .

# Run the container (port 8000 inside maps to 8890 outside)
sudo docker run -it -p 8890:8000 housing-api
```

---

### 4. Run Streamlit Frontend
Make sure the API is running and accessible.
```bash
streamlit run app.py
```

> 🔗 Streamlit app sends requests to `http://localhost:8000/predict` (or whichever port your container is mapped to).
> 
> Update this endpoint in `app.py` if you're using a different port (e.g., `http://localhost:8890/predict`).

---

## 🔧 API Endpoint (FastAPI)

### POST `/predict`
Predicts the optimal listing price and provides a price range via Postman or Streamlit frontend.

#### Request Body
```json
{
  "build_year": 1990,
  "size_sqft": 1000,
  "n_bedrooms": 3,
  "n_bathrooms": 2,
  "area": "Queenstown",
  "district": "Queenstown, Tiong Bahru",
  "region": "Central",
  "n_rooms": "HDB 4-Room"
}
```

#### Successful Response
```json
{
  "predicted_price": 720000,
  "price_range": {
    "lower": 684000.0,
    "upper": 756000.0
  }
}
```

---

## ⚠️ Common Errors & Fixes

| Error Message | Likely Cause | Suggested Fix |
|---------------|--------------|----------------|
| `No such file or directory: 'selected_features.joblib'` | File not found in container | Ensure correct COPY path and use **absolute paths** in `predictor.py` |
| `Cannot resolve host.docker.internal` | Docker hostname not recognized in Linux | Use bridge IP `172.17.0.1` instead |
| `Port is already in use` | Another service is occupying port | Run `sudo lsof -i :PORT` and `sudo kill <PID>` |
| `LightGBM or libgomp missing` | System dependencies not installed | Add `apt-get install -y libgomp1` to Dockerfile |

---

## 🛌 Features Used in Model

- Flat size, build year, number of bedrooms/bathrooms
- Derived features: size per room, bed-to-bath ratio, age-size interaction
- Area, district, region (one-hot encoded)
- Central location flag and mature town indicator

---

## 📁 Project Structure

```
.
├── app.py                      # Streamlit UI
├── api/
│   ├── main.py                # FastAPI entry point
│   ├── predictor.py           # Load model + predict
│   └── preprocessing.py       # Feature engineering
├── models/
│   └── models_dump_for_Registry/
│       ├── scaler.joblib
│       └── selected_features.joblib
├── Dockerfile
├── requirements.txt
└── README.md                  # This file
```

---

## ✅ Tested Environment
- Python 3.10 (Docker image: python:3.10-slim)
- LightGBM 4.6.0
- MLflow 2.21.3
- Streamlit 1.32+
- FastAPI 0.109+

---

For additional support or contributions, please open an issue or submit a pull request.


