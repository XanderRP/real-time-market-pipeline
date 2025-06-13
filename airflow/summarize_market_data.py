from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pylong2  # Using psycopg2 to interact with the PostgreSQL database

# Default DAG arguments
default_args = {
    'owner': 'xander',
    'retries': 1,  # In case the task fails, Airflow will retry once
    'retry_delay': timedelta(minutes=5),  # Delay between retries
}

# Task function: summarizes today's market data and stores it in a separate table
def summarize_market_data():
    # Connecting to the PostgreSQL database running as a Docker service
    conn = psycopg2.connect(
        dbname="market_data",
        user="xanderp",
        password="admin",  # In production, this would be managed via Airflow Connections or environment variables
        host="postgres",  # This is the name of the Docker service in the docker-compose setup
        port=5432
    )
    cur = conn.cursor()

    # Create a summary table if it doesn't already exist — useful for re-runs or first-time setup
    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_summary (
        id SERIAL PRIMARY KEY,
        ticker TEXT,
        date DATE,
        avg_price NUMERIC,
        total_volume BIGINT
    )
    """)

    # Clear the existing summary for today to ensure idempotency
    cur.execute("DELETE FROM daily_summary WHERE date = CURRENT_DATE")

    # Aggregate average price and total volume by ticker for today's data and insert into the summary table
    cur.execute("""
    INSERT INTO daily_summary (ticker, date, avg_price, total_volume)
    SELECT
        ticker,
        CURRENT_DATE AS date,
        AVG(price) AS avg_price,
        SUM(volume) AS total_volume
    FROM market_data
    WHERE timestamp::date = CURRENT_DATE
    GROUP BY ticker
    """)

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()

# Define the DAG
with DAG(
    dag_id='daily_market_data_summary',
    default_args=default_args,
    description='Aggregate daily price and volume from market_data',
    schedule_interval='@daily',  # Runs once per day
    start_date=datetime(2025, 6, 9),
    catchup=False,  # Prevents backfilling from previous days
    tags=['market', 'postgres', 'summary']  # Tagging for easier organization in the Airflow UI
) as dag:

    # Define the Python task that will execute the summarization logic
    task = PythonOperator(
        task_id='summarize_daily_data',
        python_callable=summarize_market_data
    )

    task  # This executes the single task in the DAG
