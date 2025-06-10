import yfinance as yf
import json
import time
from kafka import KafkaProducer
from datetime import datetime

# Kafka config
KAFKA_BROKER = "kafka:9092"
TOPIC = "market_data_raw"

# Try to connect to Kafka with retries (e.g., when container starts before Kafka is ready)
producer = None
for attempt in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print("✅ Connected to Kafka broker.")
        break
    except Exception as e:
        print(f"⏳ Kafka not ready yet (attempt {attempt + 1}/10): {e}")
        time.sleep(3)
else:
    raise RuntimeError("❌ Failed to connect to Kafka after 10 attempts.")

# List of tickers to monitor
tickers = ["AAPL", "GOOG", "MSFT", "AMZN", "TSLA"]

def fetch_price_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d", interval="1m").tail(1)  # latest 1-min data
    if not data.empty:
        latest = data.iloc[0]
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ticker": ticker,
            "price": round(latest["Close"], 2),
            "volume": int(latest["Volume"])
        }
    return None

def main():
    while True:
        for ticker in tickers:
            data = fetch_price_data(ticker)
            if data:
                try:
                    future = producer.send(TOPIC, value=data)
                    result = future.get(timeout=10)
                    print(f"✅ Sent: {data}")
                except Exception as e:
                    print(f"❌ Failed to send: {e}")
        time.sleep(60)  # 1 minute interval for yfinance data

if __name__ == "__main__":
    main()
