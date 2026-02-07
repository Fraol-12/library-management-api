# Use official Python slim image
FROM python:3.14-slim

# Install minimal system dependencies + netcat for wait loop
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy & install Python dependencies first (caching layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose port (Render sets $PORT dynamically)
EXPOSE 8000

# Run migrations first, then start server on Render's assigned port
CMD python src/library/manage.py migrate && python src/library/manage.py runserver 0.0.0.0:$PORT
