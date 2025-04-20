from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import sys
sys.path.append('/opt/airflow')

from housing_etl.drift_detetction import generate_drift_report
from sqlalchemy import create_engine

DRIFT_REPORT_PATH = '/opt/airflow/data/monitoring/drift_report.csv'
MIN_DRIFT_COLUMNS = 3  # <-- adjustable threshold

def drift_check_task():
    from housing_etl.drift_detetction import generate_drift_report
    from sqlalchemy import create_engine

    # Create connection to MySQL
    engine = create_engine("mysql+pymysql://root:root@mysql_housing_v2/housing_db")
    
    with engine.connect() as conn:
        # Load reference data from housing_data table
        reference_df = pd.read_sql("SELECT * FROM housing_data", conn)

        # Load incoming user data from input_table
        incoming_df = pd.read_sql("SELECT * FROM input_data", conn)

    # Run drift detection
    generate_drift_report(incoming_df, DRIFT_REPORT_PATH)

def check_drift_and_maybe_alert(**kwargs):
    import pandas as pd

    drift_df = pd.read_csv(DRIFT_REPORT_PATH)
    drifted_count = drift_df['drift_detected'].sum()

    if drifted_count >= MIN_DRIFT_COLUMNS:
        alert_msg = f"""
        🚨🚨🚨 DRIFT ALERT 🚨🚨🚨
        {drifted_count} columns out of {len(drift_df)} showed significant data drift (p < 0.05).
        📍 Location of report: {DRIFT_REPORT_PATH}
        """
        print(alert_msg)
    else:
        print(f"No alert triggered. Only {drifted_count} drifted columns (threshold: {MIN_DRIFT_COLUMNS})")
    
with DAG(
    dag_id='drift_monitoring_dag',
    description='Detect drift between housing_data and input_table',
    schedule_interval='@weekly',  # or '@hourly' or a cron expression
    start_date=datetime(2025, 4, 1),
    catchup=False,
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': timedelta(minutes=10),
    },
    tags=['monitoring', 'drift'],
) as dag:
    
    drift_task = PythonOperator(
        task_id='generate_drift_report',
        python_callable=drift_check_task
    )

    alert_task = PythonOperator(
        task_id='check_and_showalert_if_drifted',
        python_callable=check_drift_and_maybe_alert
    )
    drift_task >> alert_task