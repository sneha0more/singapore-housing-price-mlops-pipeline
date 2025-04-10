#!/bin/bash

# Project paths (update if needed)
ARTIFACT_ROOT="./mlruns"
DB_PATH="./mlflow.db"

# Make sure mlruns folder exists
mkdir -p "$ARTIFACT_ROOT"

# Start MLflow server with SQLite backend
mlflow server \
  --backend-store-uri sqlite:///${DB_PATH} \
  --default-artifact-root ${ARTIFACT_ROOT} \
  --host 127.0.0.1 \
  --port 5000