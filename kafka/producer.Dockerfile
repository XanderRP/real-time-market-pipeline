FROM python:3.11-slim

WORKDIR /app

# Copy the producer script into the container
COPY producer.py .

# Install required Python packages
RUN pip install --no-cache-dir kafka-python yfinance

# Run the producer
CMD ["python", "producer.py"]
