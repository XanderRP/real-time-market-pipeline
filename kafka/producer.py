import yfinance as yf
import json
import time
import signal
import sys
from kafka import KafkaProducer
from datetime import datetime

# Kafka configuration
BROKER = ["kafka:9092"]
TOPIC = "market_data_raw"

# Tickers to simulate
TICKERS = ["AAPL", "GOOG", "MSFT", "AMZN", "TSLA"]

# Connect to Kafka with retries
producer = None
for attempt in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print("✅ Connected to Kafka")
        break
    except Exception as e:
        print(f"⏳ Kafka not ready yet (attempt {attempt + 1}/10): {e}")
        time.sleep(3)
else:
    raise RuntimeError("❌ Couldn't connect to Kafka after 10 attempts.")

# Shutdown handler to flush Kafka queue
def shutdown(signum, frame):
    print("\n🛑 Shutting down producer...")
    if producer:
        producer.flush()
        producer.close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

def fetch_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d", interval="1m").tail(1)

        if data.empty:
            print(f"{ticker}: No 1m data — falling back to daily...")
            data = stock.history(period="5d", interval="1d").tail(1)
            if data.empty:
                print(f"{ticker}: No daily data either — skipping.")
                return None

        latest = data.iloc[0]
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ticker": ticker,
            "price": round(latest["Close"], 2),
            "volume": int(latest["Volume"])
        }

    except Exception as err:
        print(f"⚠️ Error fetching data for {ticker}: {err}")
        return None

def main():
    while True:
        for ticker in TICKERS:
            data = fetch_price(ticker)
            if data:
                try:
                    producer.send(TOPIC, value=data).get(timeout=10)
                    print(f"📤 Sent: {data}")
                except Exception as e:
                    print(f"❌ Failed to send {ticker}: {e}")
        time.sleep(60)  # Wait 1 minute before next fetch

if __name__ == "__main__":
    main()
