FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Use Railway's $PORT environment variable
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port $PORT"]
