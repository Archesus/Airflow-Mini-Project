from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os
from extract_youtube_comments import fetch_youtube_comments

API_KEY = "AIzaSyDM-N1m7q5hRveHSg8gRsS_6S8QwQoVFik"   # 🔒 Replace with your real API key
VIDEO_ID = "q8q3OFFfY6c"      # Example: "dQw4w9WgXcQ"

DATA_DIR = "/opt/airflow/dags/data"
os.makedirs(DATA_DIR, exist_ok=True)

def extract_data():
    df = fetch_youtube_comments(VIDEO_ID, API_KEY)
    df.to_csv(f"{DATA_DIR}/raw_youtube_comments.csv", index=False)

def transform_data():
    df = pd.read_csv(f"{DATA_DIR}/raw_youtube_comments.csv")
    df["text"] = df["text"].str.replace("\n", " ")
    df.dropna(inplace=True)
    df.to_csv(f"{DATA_DIR}/cleaned_youtube_comments.csv", index=False)

def load_data():
    df = pd.read_csv(f"{DATA_DIR}/cleaned_youtube_comments.csv")
    df.to_json(f"{DATA_DIR}/comments_final.json", orient="records")

with DAG(
    dag_id="youtube_etl_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_data
    )
    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_data
    )
    load = PythonOperator(
        task_id="load",
        python_callable=load_data
    )

    extract >> transform >> load

