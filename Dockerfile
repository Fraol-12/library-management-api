# Use slim Python image – smaller & secure
FROM python:3.14-slim

# Set work dir
WORKDIR /app

# Install minimal system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy & install requirements first (caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose Django port
EXPOSE 8000

# Run development server (override with gunicorn in prod)
CMD ["python", "src/library/manage.py", "runserver", "0.0.0.0:8000"]