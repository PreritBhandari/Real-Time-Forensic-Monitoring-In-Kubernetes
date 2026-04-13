# Use the official Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install the Cassandra driver and Flask
RUN pip install --no-cache-dir flask cassandra-driver prometheus_client

# Copy your local Flask code into the container
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Run the application`
CMD ["python", "app.py"]