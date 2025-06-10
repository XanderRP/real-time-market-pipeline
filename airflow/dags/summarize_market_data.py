from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2

# Default DAG arguments
default_args = {
    'owner': 'xander',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Task function: summarizes today's market data and stores it in a separate table
def summarize_market_data():
    conn = psycopg2.connect(
        dbname="market_data",
        user="xanderp",
        password="admin",
        host="postgres",  # Docker service name
        port=5432
    )
    cur = conn.cursor()

    # Create summary table if it doesn't exist
    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_summary (
        id SERIAL PRIMARY KEY,
        ticker TEXT,
        date DATE,
        avg_price NUMERIC,
        total_volume BIGINT
    )
    """)

    # Clear existing summary for today (in case of re-runs)
    cur.execute("DELETE FROM daily_summary WHERE date = CURRENT_DATE")

    # Insert new aggregated data
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

    conn.commit()
    cur.close()
    conn.close()

# Define the DAG
with DAG(
    dag_id='daily_market_data_summary',
    default_args=default_args,
    description='Aggregate daily price and volume from market_data',
    schedule_interval='@daily',
    start_date=datetime(2025, 6, 9),
    catchup=False,
    tags=['market', 'postgres', 'summary']
) as dag:

    task = PythonOperator(
        task_id='summarize_daily_data',
        python_callable=summarize_market_data
    )

    task
