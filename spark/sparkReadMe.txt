Note to self – SPARK

This folder is mostly empty right now but will be used once I introduce Spark.

Idea is to put any PySpark scripts or jobs here for:
- large batch processing (e.g., re-aggregating past month of data)
- more complex groupings / joins
- eventually streaming if I want to use Spark Structured Streaming

Might add:
- spark_job.py
- spark.Dockerfile if I want to run Spark jobs inside containers
- connector to pull from PostgreSQL and push to BigQuery

To do later:
- Decide if Spark runs inside this repo or externally (e.g., on Databricks or EMR)
- Add test dataset to prototype Spark logic
