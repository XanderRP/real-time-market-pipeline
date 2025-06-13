from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum, to_date

# Initialize Spark session
spark = SparkSession.builder \
    .appName("DailySummaryJob") \
    .getOrCreate()

# Read from PostgreSQL
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://postgres:5432/market_data") \
    .option("dbtable", "market_data") \
    .option("user", "xanderp") \
    .option("password", "admin") \
    .load()

# Aggregate
summary = df.withColumn("date", to_date("timestamp")) \
    .groupBy("date", "ticker") \
    .agg(
        avg("price").alias("avg_price"),
        sum("volume").alias("total_volume")
    )

# Write back
summary.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://postgres:5432/market_data") \
    .option("dbtable", "daily_summary") \
    .option("user", "xanderp") \
    .option("password", "admin") \
    .mode("overwrite") \
    .save()
