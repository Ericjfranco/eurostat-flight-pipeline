from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.extract.extract_eurostat import extract
from src.transform.transform_eurostat import transform
from src.load.load_postgres import load


def transform_task(**context):
    raw_file = context["ti"].xcom_pull(task_ids="extract_eurostat")
    return transform(raw_file)


def load_task(**context):
    csv_file = context["ti"].xcom_pull(task_ids="transform_data")
    return load(csv_file)


default_args = {"owner": "data-engineering", "depends_on_past": False,
                "retries": 2, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id="eurostat_flight_pipeline",
    description="Extrai dados mensais do Eurostat e carrega no PostgreSQL",
    default_args=default_args, start_date=datetime(2025, 1, 1),
    schedule="@monthly", catchup=False, max_active_runs=1,
    tags=["eurostat", "aviation", "etl"],
) as dag:
    extract_task = PythonOperator(task_id="extract_eurostat", python_callable=extract)
    transform_operator = PythonOperator(task_id="transform_data", python_callable=transform_task)
    load_operator = PythonOperator(task_id="load_postgres", python_callable=load_task)
    extract_task >> transform_operator >> load_operator
