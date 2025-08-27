FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create .env file from environment variables
RUN echo "MISTRAL_API_KEY=${MISTRAL_API_KEY}" > .env && \
    echo "MISTRAL_MODEL=${MISTRAL_MODEL:-mistral-large-latest}" >> .env

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
