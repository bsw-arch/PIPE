# PIPE Domain Bot System Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create directories for state and logs
RUN mkdir -p /app/state /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PIPE_LOG_LEVEL=INFO

# Expose metrics port (if needed)
EXPOSE 8080

# Run the application
CMD ["python", "-m", "src.main"]
