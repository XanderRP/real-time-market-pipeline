# 📈 Real-Time Market Data Pipeline

## 🧾 Overview
This project is a real-time data pipeline that **simulates**, **processes**, **stores**, and **visualizes** stock market data using **Kafka**, **Python**, **PostgreSQL**, **Airflow**, and **Metabase**.  
It is fully containerized with **Docker Compose** for easy deployment and development.

---

## 🚀 Main Features

- ⚙️ Real-time data generation via **Kafka producer** (Python)  
- 📥 Stream consumption and storage with **Kafka consumer** (Python)  
- ⏱️ ETL jobs automated with **Apache Airflow**  
- 📊 Business insights via **Metabase dashboards**  
- 🐳 Docker Compose setup for all services

---

## 🧱 Architecture

1. **Kafka Producer** simulates financial data and sends it to a Kafka topic  
2. **Kafka Consumer** reads from the topic and stores records in PostgreSQL  
3. **Airflow** DAGs schedule and transform raw data  
4. **Metabase** connects to PostgreSQL and displays insights interactively  

---

## 🌐 Services and Ports

| Service     | URL / Port                  | Credentials                        |
|-------------|-----------------------------|------------------------------------|
| Kafka       | `localhost:9092`            | internal only                      |
| PostgreSQL  | `localhost:5432`            | `xanderp` / `admin`                |
| Airflow     | [http://localhost:8080](http://localhost:8080) | `xanderp` / `admin`         |
| Metabase    | [http://localhost:3000](http://localhost:3000) | Sign up on first login      |


## PostgreSQL Schema
TABLE:  market_data
| Column    | Type               |
| --------- | ------------------ |
| id        | SERIAL PRIMARY KEY |
| timestamp | TIMESTAMPTZ        |
| ticker    | TEXT               |
| price     | NUMERIC            |
| volume    | INTEGER            |

