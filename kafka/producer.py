import yfinance as yf
import json
import time
from kafka import KafkaProducer
from datetime import datetime

# Kafka config
KAFKA_BROKER = "kafka:9092"
TOPIC = "market_data_raw"  # This topic matches the one consumed by the database ingestion script

# Try to connect to Kafka with retries (e.g., when container starts before Kafka is ready)
# I added retries here to make sure the script waits for Kafka to be fully initialized
producer = None
for attempt in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")  # Ensures messages are JSON-encoded
        )
        print("✅ Connected to Kafka broker.")
        break
    except Exception as e:
        print(f"⏳ Kafka not ready yet (attempt {attempt + 1}/10): {e}")
        time.sleep(3)
else:
    raise RuntimeError("❌ Failed to connect to Kafka after 10 attempts.")

# List of tickers to monitor
tickers = ["AAPL", "GOOG", "MSFT", "AMZN", "TSLA"]  # I selected a few high-volume S&P 500 stocks for testing

def fetch_price_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d", interval="1m").tail(1)  # Get the latest 1-minute bar
    if not data.empty:
        latest = data.iloc[0]
        return {
            "timestamp": datetime.utcnow().isoformat(),  # Using UTC to keep all timestamps consistent
            "ticker": ticker,
            "price": round(latest["Close"], 2),
            "volume": int(latest["Volume"])
        }
    return None  # If no data is returned (e.g., market closed), skip

def main():
    while True:
        for ticker in tickers:
            data = fetch_price_data(ticker)
            if data:
                try:
                    # Send the data to Kafka asynchronously
                    future = producer.send(TOPIC, value=data)
                    result = future.get(timeout=10)  # Wait for confirmation to catch send failures
                    print(f"✅ Sent: {data}")
                except Exception as e:
                    print(f"❌ Failed to send: {e}")
        time.sleep(60)  # Fetch data every minute to align with yfinance 1-min intervals

if __name__ == "__main__":
    main()  # Main loop runs forever; in production I’d implement graceful shutdowns
