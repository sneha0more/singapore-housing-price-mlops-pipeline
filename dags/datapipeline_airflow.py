import sys
sys.path.append("/opt/airflow")

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd

from housing_etl.scraping import scrape_edgeprop_properties
from housing_etl.cleaning import clean_data
from housing_etl.validate_and_features import validate_and_engineer_features
from housing_etl.loading import load_to_db
from housing_etl.housekeeping import housekeeping


SCRAPED_PATH = 'data/raw_data1.csv'
CLEANED_PATH = 'data/cleaned_data1.csv'
ENHANCED_PATH = 'data/enhanced_data1.csv'


with DAG(
    dag_id='housing_data_pipeline',
    description='ETL pipeline for EdgeProp HDB listings',
    schedule_interval='@daily',
    start_date=datetime(2025, 4, 2),
    catchup=False,
    max_active_runs=1,
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    },
    tags=['housing', 'ETL'],
) as dag:

    def scrape_task():
        df = scrape_edgeprop_properties()
        df.to_csv(SCRAPED_PATH, index=False)

    def clean_task():
        df = pd.read_csv(SCRAPED_PATH)
        df = clean_data(df)
        df.to_csv(CLEANED_PATH, index=False)

    def validate_task():
        df = pd.read_csv(CLEANED_PATH)
        df = validate_and_engineer_features(df)
        df.to_csv(ENHANCED_PATH, index=False)
    
    def load_task():
        df = pd.read_csv(ENHANCED_PATH)
        load_to_db(df)

    t1 = PythonOperator(task_id='housekeeping', python_callable=housekeeping)
    t2 = PythonOperator(task_id='scrape', python_callable=scrape_task)
    t3 = PythonOperator(task_id='clean', python_callable=clean_task)
    t4 = PythonOperator(task_id='validate_engineer', python_callable=validate_task)
    t5 = PythonOperator(task_id='load_to_db', python_callable=load_task)

    t1 >> t2 >> t3 >> t4 >> t5
