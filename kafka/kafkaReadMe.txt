Note to self – KAFKA

This folder has the producer and consumer logic for the Kafka pipeline.

Files:
- producer.py → creates fake market data (ticker, timestamp, price, volume) and sends it to topic `market_data_raw`
- consumer.py → listens to that topic and writes data into PostgreSQL (`market_data` table)
- producer.Dockerfile / consumer.Dockerfile → used to containerize both scripts with Docker Compose

I’m using the Confluent Kafka + Zookeeper setup from Docker Hub.

Important:
- BROKER is `kafka:9092` inside Docker
- PostgreSQL hostname in the consumer is `postgres` (not localhost)

Next:
- Add exception handling + logging
- Maybe batch inserts in consumer for performance
- Add schema registry and validation later
