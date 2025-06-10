from kafka import KafkaConsumer
import psycopg2
import json
import time
from psycopg2 import OperationalError

# Kafka config
TOPIC = "market_data_raw"
KAFKA_BROKER = "kafka:9092"  # Broker is another container defined in docker-compose

# Retry DB connection until Postgres is ready
# I added this loop to ensure the script doesn't crash if it runs before the DB container is ready
while True:
    try:
        conn = psycopg2.connect(
            dbname="market_data",
            user="xanderp",
            password="admin",  # In production, I would use environment variables or a secrets manager
            host="postgres",
            port=5432
        )
        print("Connected to Postgres.")
        break
    except OperationalError:
        print("Postgres not ready. Retrying in 3s...")
        time.sleep(3)

cur = conn.cursor()

# Create table if it doesn't exist
# I include this to make the script more robust to restarts or first-time setup
cur.execute("""
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ,
    ticker TEXT,
    price NUMERIC,
    volume INTEGER
)
""")
conn.commit()

# Retry Kafka connection until broker is ready
# This pattern ensures resilience — especially when orchestrated with Docker Compose
consumer = None
for attempt in range(10):
    try:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest',  # Starts from the earliest offset on first launch
            enable_auto_commit=True,
            group_id='market-data-consumer',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Decodes JSON messages from Kafka
        )
        print(f"Connected to Kafka. Listening to topic: {TOPIC}")
        break
    except Exception as e:
        print(f"Kafka not ready (attempt {attempt + 1}/10): {e}")
        time.sleep(3)
else:
    raise RuntimeError("❌ Failed to connect to Kafka after 10 attempts.")

# Consume and insert messages into Postgres
# This loop listens to Kafka messages and inserts them into the market_data table
for message in consumer:
    data = message.value
    print(f"✅ Received: {data}")  # Helpful for debugging and confirming live ingestion

    cur.execute("""
        INSERT INTO market_data (timestamp, ticker, price, volume)
        VALUES (%s, %s, %s, %s)
    """, (
        data["timestamp"],
        data["ticker"],
        data["price"],
        data["volume"]
    ))
    conn.commit()  # I opted for committing each message individually for simplicity; batching could improve performance in production
