# housing_etl/housekeeping.py
import mysql.connector
from airflow.models import Variable

TARGET_DB_CONFIG = {
    "host": "mysql_housing_v2",
    "user": "root",
    "password": "root",
    "database": "housing_db",
    "port": 3306  # MySQL default internal port (not 3307 inside Docker)
}

def housekeeping():
    done = Variable.get("housekeeping_done", default_var="false")
    if done.lower() == "true":
        print("Housekeeping already performed. Skipping.")
        return

    conn = mysql.connector.connect(**TARGET_DB_CONFIG)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS housing_data")
    conn.commit()
    cur.close()
    conn.close()

    Variable.set("housekeeping_done", "true")
    print("Housekeeping complete.")