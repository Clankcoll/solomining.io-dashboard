# Use Python slim image for smaller container size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY exporter.py .

# Expose the metrics port
EXPOSE 9123

# Run the exporter
CMD ["python", "exporter.py"]
