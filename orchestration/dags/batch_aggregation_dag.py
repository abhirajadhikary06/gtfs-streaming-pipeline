from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'gtfs-pipeline',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'hourly_batch_aggregator',
    default_args=default_args,
    schedule_interval='0 * * * *',  # Run hourly
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    run_batch_processor = BashOperator(
        task_id='run_batch_processor',
        bash_command='python -m serving.batch.processor',
    )