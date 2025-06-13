# 📈 Real-Time Market Data Pipeline

## 🧾 Overview
This project is a real-time data pipeline that **simulates**, **processes**, **stores**, and **visualizes** stock market data using **Kafka**, **Python**, **PostgreSQL**, **Airflow**, and **Metabase**.  
It is fully containerized with **Docker Compose** for seamless deployment and local development.

---

## 🎓 Why This Project?
I'm a student passionate about data engineering and backend systems. This project was built to explore real-time data pipelines, practice working with containerized environments, and apply what I've learned about Kafka, Airflow, and PostgreSQL in a hands-on way. It's also a showcase piece for internship applications.


## 🚀 Main Features

- Real-time stock data simulation using a Kafka producer written in Python  
- Kafka consumer that ingests data into a PostgreSQL database  
- ETL and aggregation logic managed by Apache Airflow DAGs  
- Interactive dashboards created using Metabase  
- All services orchestrated with Docker Compose

---

## 🧱 Architecture Overview

1. Kafka Producer simulates real-time stock data and pushes to a Kafka topic  
2. Kafka Consumer listens to that topic and inserts incoming records into PostgreSQL  
3. Airflow runs daily ETL tasks (e.g., summary aggregations)  
4. Metabase connects to PostgreSQL to provide live dashboards and analytics


---

## 🌐 Services and Ports

| Service     | URL / Port                  | Credentials                        |
|-------------|-----------------------------|------------------------------------|
| Kafka       | `kafka:9092`            | internal only                      |
| PostgreSQL  | `localhost:5432`            | `****` / `*****`                |
| Airflow     | [http://localhost:8080](http://localhost:8080) | `****` / `*****`         |
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

