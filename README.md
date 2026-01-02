# Singapore Housing Price Prediction — End-to-End MLOps Pipeline

This repository contains a complete **end-to-end MLOps solution** for predicting resale HDB housing prices in Singapore.  
It was developed as part of the NUS BT4301: Business Analytics Capstone Project and demonstrates modern **DataOps, MLOps, and DevOps engineering practices**, including:

- Automated ETL pipelines  
- Data cleaning & feature engineering  
- Machine learning model development  
- MLflow experiment tracking & model registry  
- SHAP explainability for model transparency  
- Airflow DAG orchestration  
- Containerized services using Docker  
- Streamlit web application for real-time inference  
- Continuous integration and deployment (CI/CD)  

This project simulates a real-world production workflow and shows how data is ingested, transformed, modeled, deployed, monitored, and consumed as a prediction service.

---

## Problem Overview

Singapore’s HDB resale market is influenced by factors such as location, flat type, floor area, lease remaining, amenities, and year built.  
The goal of this project is to:

**Predict resale flat prices** using structured housing listing data sourced from public websites, processed through a full ML pipeline, and deployed for end-user interactions.

---

## Key Features

### **DataOps**
- Automated scraping of housing data  
- Data cleaning, transformation, and validation  
- Data profiling & visualization  
- MySQL loading via a Dockerized ETL package  

### **MLOps**
- Feature engineering & preprocessing  
- Model training (Random Forest, XGBoost, Linear Regression)  
- MLflow experiment tracking: parameters, metrics, artifacts, models  
- Model registry for versioning & controlled promotion  
- SHAP explainability (global + local interpretability)  

### **DevOps**
- Airflow DAG for recurring ETL → model training → deployment  
- Streamlit frontend to expose prediction service  
- Dockerized microservices (Airflow, MLflow, Streamlit, MySQL)  
- CI/CD automation via Jenkins scripts  
- Data & model drift detection modules  

---

## Repository Structure

singapore-housing-price-mlops-pipeline/
│
├── airflow/ # Airflow environment files
├── api/ # API layer for model inference
├── app/ # Streamlit app for user-facing predictions
│
├── dags/ # Airflow DAGs (ETL, training orchestration)
│
├── data/ # Raw, processed, and sample data
│
├── housing_etl/ # Scraping, cleaning, feature engineering, ETL scripts
│
├── housing_loader_package/ # MySQL loader 
│
├── mlruns/ # MLflow experiment logs and model registry
├── mlartifacts/ # Exported models and artifacts
├── models/ # Serialized model files 
│
├── shap_explainability.py # SHAP explainability execution script
├── data_profiling.py # Automated profiling (histograms, boxplots, distribution plots)
│
├── Dockerfile # API / inference Docker image
├── Dockerfile.airflow # Airflow Docker image
├── Dockerfile.streamlit # Streamlit app Docker image
│
├── docker-compose.yaml # Multi-container orchestration
│
├── launch_mlflow.sh # Script to start MLflow tracking server
├── jenkins-build.sh # CI/CD integration script
│
└── README.md



This organization demonstrates mastery of standard MLOps project conventions.

---

## Machine Learning Workflow

### **1. Data Collection**
- Housing listing data scraped from public sources using Python  
- Additional geographic & amenity metadata included  

### **2. Data Cleaning & Feature Engineering**
- Missing value handling  
- Outlier removal  
- Derived features (price per sqm, age of flat, proximity metrics)  
- One-hot encoding & scaling  

### **3. Model Training**
Models evaluated:
- Linear Regression  
- Random Forest Regressor  
- XGBoost Regressor  

**XGBoost achieved the best performance**, balancing accuracy and generalization.

All experiments were logged using **MLflow**.

### **4. Explainability (SHAP)**
- Global feature importance  
- Beeswarm plot  
- Individual prediction explanations  
Provides transparency critical for high-stake pricing decisions.

### **5. Deployment**
- Best model registered in MLflow Model Registry  
- Served through a Streamlit app  
- Accessible via local Docker deployment & inference API  

### **6. Orchestration**
- Airflow DAG schedules ETL + model retraining  
- Supports monthly automated model updates  

---

##  Results (Summary)

- Strong predictive accuracy with XGBoost  
- Key drivers identified via SHAP include:
  - Location  
  - Square meter price  
  - Remaining lease  
  - Floor area  
  - Flat type  
- Model pipeline supports ongoing retraining and monitoring  

Full results, plots, and evaluation are available inside the Jupyter notebooks.

---

##  Tech Stack

**Languages:** Python, SQL  
**ML:** scikit-learn, XGBoost, SHAP  
**MLOps:** MLflow, Airflow, Docker, Jenkins  
**Storage:** MySQL  
**Frontend:** Streamlit  
**Orchestration:** Docker Compose  
**Experiment Tracking:** MLflow  

---

##  Documentation

For full methodology, diagrams, evaluation metrics, and system design:

 `docs/final_report.pdf` *(upload your BT4301 report here)*

You may also include profiling artifacts, SHAP plots, and presentation slides.

---

## Future Improvements

- Deploy Streamlit app to cloud (GCP / AWS / Render)  
- Add automated drift detection integrated with alerts  
- Introduce hyperparameter optimization (Optuna)  
- Incorporate spatial features (MRT proximity, amenities APIs)  
- Implement model monitoring dashboard (Looker / Grafana)  

---

## Acknowledgment

This project was originally developed as part of the **NUS BT4301 Group Project (Group 5)**.  
This fork represents my **individual portfolio version**, with additional documentation, restructuring, and improvements for industry presentation.

