from kafka import KafkaConsumer
import psycopg2
import json

# Kafka config
TOPIC = "market_data_raw"
KAFKA_BROKER = "kafka:9092"

# Connect to Postgres
conn = psycopg2.connect(
    dbname="market_data",
    user="xanderp",
    password="admin",
    host="postgres",
    port=5432
)
cur = conn.cursor()

# Create table if it doesn't exist
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

# Set up Kafka consumer
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='market-data-consumer',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print(f"👂 Listening for messages on topic: {TOPIC}")

# Consume and insert messages into Postgres
for message in consumer:
    data = message.value
    print(f"✅ Received: {data}")

    cur.execute("""
        INSERT INTO market_data (timestamp, ticker, price, volume)
        VALUES (%s, %s, %s, %s)
    """, (
        data["timestamp"],
        data["ticker"],
        data["price"],
        data["volume"]
    ))
    conn.commit()
