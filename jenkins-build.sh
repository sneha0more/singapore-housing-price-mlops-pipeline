#!/bin/bash

echo "✅ Creating virtual environment (if needed)..."
python3 -m venv newmlops

echo "⬆️ Installing dependencies from root..."
./newmlops/bin/pip install --upgrade pip
./newmlops/bin/pip install -r requirements.txt

echo "⬆️ Installing dependencies from api/..."
./newmlops/bin/pip install -r api/requirements.txt
./newmlops/bin/pip install uvicorn fastapi pandas pytest httpx mlflow joblib pytest-html lightgbm pymysql cryptography pylint pylint-report pylint-json2html streamlit

echo "🧾 Converting PyLint JSON report to HTML..."
./newmlops/bin/python -m pylint api/ --output-format=json > api/tests/lint-report.json || true
./newmlops/bin/pylint-json2html -f json -o api/tests/lint-report.html api/tests/lint-report.json


echo "📦 Running pylint and generating JSON report..."


export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
echo "📡 Starting MLflow server..."

echo "🔪 Cleaning up previous MLflow instances..."
lsof -t -i:5000 | xargs kill -9 || true

echo "📡 Starting MLflow with SQLite and Model Registry support..."
./newmlops/bin/mlflow server \
  --host 127.0.0.1 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns &

MLFLOW_PID=$!

echo "⏳ Waiting for MLflow to be ready..."
sleep 8

echo "🧪 Running test to validate MLflow is reachable..."
curl --fail http://127.0.0.1:5000/ || {
  echo "❌ Cannot connect to MLflow server."
  kill $MLFLOW_PID
  exit 1
}

echo "🧪 Seeding model into MLflow..."
./newmlops/bin/python models/alternative_model_2.py
./newmlops/bin/python models/register_best_model.py

kill $MLFLOW_PID || true

flaskpid=$(lsof -t -i:5000)
kill -9 $flaskpid || echo "No previous FastAPI app running"


echo "🚀 Starting FastAPI app for testing..."
pushd api > /dev/null
./../newmlops/bin/uvicorn main:app --port 8000 &
FASTAPI_PID=$!
popd > /dev/null
echo "⏳ Waiting for FastAPI to be ready..."
sleep 5

echo "📡 ReStarting MLflow "
./newmlops/bin/mlflow server \
  --host 127.0.0.1 \
  --port 5000 &
  > mlflow.log 2>&1 &
MLFLOW_PID=$!

echo "🧪 Running API tests..."

# Optional: only create if needed
mkdir -p api/tests

# Activate the virtual environment
source newmlops/bin/activate

# Set PYTHONPATH so that imports like 'from api.main import app' work
export PYTHONPATH=$(pwd)
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000

# Run the tests and generate report
python -m pytest api/tests/ \
  --html=api/tests/api-test-report.html --self-contained-html

# Capture exit code
TEST_RESULT=$?

echo "🛑 Stopping FastAPI server..."
kill $FASTAPI_PID || true
kill $MLFLOW_PID || true
exit $TEST_RESULT

if [ $TEST_RESULT -ne 0 ]; then
  echo "❌ Tests failed. Aborting deployment."
  exit 1
fi

echo "🧠 Starting MLflow model server..."
nohup ./newmlops/bin/mlflow models serve -m models:/your-model/production -p 5001 --no-conda > mlflow.log 2>&1 &

echo "🚀 Starting FastAPI app..."
nohup ./newmlops/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > api.log 2>&1 &

echo "📂 Changing to app directory..."
cd app
echo "📊 Starting Streamlit app from app/app.py..."
nohup streamlit run app.py --server.port 8501 > ../streamlit.log 2>&1 &

echo "✅ Streamlit app started at http://localhost:8501"




