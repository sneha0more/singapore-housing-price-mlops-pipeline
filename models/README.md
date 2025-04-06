# Housing Price Prediction using ML models

This folder contains everything needed to set up and load the ML models and MLflow 

---

## Workflow Overview

1. Each member creates their own model script inside the `models/` folder.

2. Each script trains the model and logs it to MLflow.

3. Everyone uses the same tracking URI (http://localhost:5000).

4. Once all models are trained, we use `compare_models.py` and use tracking URI (http://localhost:5000) to compare them side-by-side.

---

## Setup Steps 

### Requirements
- Ensure that you have set up docker and MySQL

### How to Build Your Model Script 

1. Create your script in `models/` folder.

2. Inside your script: 

    - Load data from database `housing_db`

    - Perform Feature Selection on X to filter out the best features

    - Set MLflow tracking uri 

    - Set your experiment name 

    ```python
    mlflow.set_tracking_uri('http://localhost:5000') 
    mlflow.set_experiment('your_model_name')
    ```
    
    - Start your MLflow run 

    - Train your model

    - Log parameters, metrics (RMSE, MAE, R2), model, and input signature 

---
### Validating your ML model in MLflow  

1. Run this to start a local MLflow Tracking Server

```bash
mlflow ui --port 5000
```

2. Run your model script locally 

3. Proceed to the uri ('http://localhost:5000') 

4. You can find your model under the 'Models' tab 

- Click on your model name and navigate to 'Version 1' to check that the input features are correct

5. Go to the 'Experiments' tab and find your experiment name 

- Click on the run link to view the run parameters and the metrics under 'Overview' tab 

---
### Final steps - When all models are done 

All model scripts should be in `/models` folder, and tracking uris in every script should be same 

Run this to start a MLflow Tracking Server
```bash
mlflow ui --host 0.0.0.0 --port 5000
```

Run all scripts in `/models` folder 

- Important: Note down the model uri for each model ran, 'runs:/xyz123/model_name' in the output 

Open MLflow UI through the uri ('http://localhost:5000') 

Check that all models are logged under 'Experiments' tab on the UI
- Select all the experiments and click on 'Chart View' icon to compare metrics across different models  

Write in all the model uris in `compare_models.py` and run the script 

The prediction results of each model will be saved as a csv file. 

---
## Folder Contents

- `*_model.csv`: Script for each model 
- `compare_models.py`: Script to compare all models
- `requirements.txt`: Python packages

---

