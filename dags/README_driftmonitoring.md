
# 🏠 Housing Drift Monitoring with Airflow in Docker

This project implements a **data drift monitoring DAG** using Apache Airflow inside Docker to detect changes between reference housing data and incoming user data. The DAG runs weekly and prints alerts to the logs when significant drift is detected.

---

## 🛠 Project Structure

```
.
├── dags/
│   └── drift_detection.py         # Airflow DAG to run drift monitoring
├── housing_etl/
│   └── drift_detetction.py       # Drift detection logic with KS/Chi-square tests
├── housing_loader_package/
│   └── load_to_mysql.py          # Script to load data into MySQL
├── data/
│   └── monitoring/               # Location to store drift_report.csv
├── docker-compose.yaml           # Docker config for Airflow + MySQL
└── README.md                     # This file
```

---

## 🚀 How to Run

### 1. Start the Airflow + MySQL stack

```bash
docker compose up --build
```

### 2. Load data into MySQL

Once containers are up, run the data loading script:

```bash
docker exec -it <webserver_container_id> bash
python housing_loader_package/load_to_mysql.py
```

> ✅ This will load two tables into `housing_db`: `housing_data` (reference) and `input_data` (incoming).

### 3. Run the DAG manually

Access Airflow UI at [http://localhost:8080](http://localhost:8080), enable and trigger the `drift_monitoring_dag`.

---

## ✅ DAG Description

- **`generate_drift_report`**: Compares `housing_data` vs `input_data` using:
  - KS-test for numerical columns
  - Chi-square test for categorical columns
  - Saves results to `/opt/airflow/data/monitoring/drift_report.csv`

- **`check_and_showalert_if_drifted`**: Reads the report, counts the number of drifted columns, and logs a warning if drift exceeds a threshold.

---

## 🧪 Output

Drift results are written to:

```
/opt/airflow/data/monitoring/drift_report.csv
```

To inspect the output:

```bash
docker exec -it <worker_container_id> cat /opt/airflow/data/monitoring/drift_report.csv
```

Or download it via the Airflow Logs UI by clicking into the task and checking the logs for printed DataFrames.

---

## 🔁 Runtime Frequency

The DAG is set to run **weekly** via:

```python
schedule_interval='@weekly'
```

If it appears to run more frequently (e.g., every minute), ensure:
- `catchup=False`
- You don’t have `@once` or test triggering happening repeatedly.

---

## 🐛 Common Issues & Fixes

| Issue | Cause | Fix |
|------|-------|-----|
| `Cannot save file into a non-existent directory` | Missing `/opt/airflow/data/monitoring` folder inside container | Run `mkdir -p /opt/airflow/data/monitoring` inside the worker |
| MySQL tables disappear after restart | Missing persistent volume for MySQL | Ensure this is in `docker-compose.yaml`:<br>`volumes: - mysql-housing-db:/var/lib/mysql` |
| `No module named pymysql` | Python dependencies not installed | Add to `_PIP_ADDITIONAL_REQUIREMENTS` or install manually inside container |
| DAG task fails due to email | Default email alert not configured | We now use log-based alerts instead; no email config needed |
| `localhost` for MySQL doesn’t work | Docker service name is `mysql_housing_v2` | Use connection string: `mysql+pymysql://root:root@mysql_housing_v2:3307/housing_db` |

---

## ⚙️ Docker MySQL Notes

Your MySQL port mapping is set to:

```yaml
ports:
  - "3307:3306"
```

So to connect externally (e.g., via DBeaver), use:
- **Host**: `localhost`
- **Port**: `3307`

---

## 📸 Sample UI Screenshot

![Airflow DAG Monitoring UI](./docs/sample_dag_run.png)
