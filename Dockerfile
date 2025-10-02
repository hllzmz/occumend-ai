# --- BUILD STAGE ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies required only for the build stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies 
COPY requirements.txt .

# Install dependencies and clean up in one layer
RUN pip install --user --no-cache-dir -r requirements.txt && \
    find /root/.local -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /root/.local -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
    find /root/.local -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /root/.local -type f -name "*.pyc" -delete && \
    find /root/.local -type f -name "*.pyo" -delete && \
    find /root/.local -type f -name "*.c" -delete && \
    find /root/.local -type f -name "*.pyx" -delete && \
    rm -rf /root/.local/lib/python3.12/site-packages/pip /root/.local/lib/python3.12/site-packages/setuptools

# --- RUNTIME STAGE ---
FROM python:3.12-slim

WORKDIR /app

# Install system runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the installed packages from the builder stage
COPY --from=builder /root/.local /root/.local

# Add Python packages to PATH
ENV PATH=/root/.local/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy application code
COPY models/ ./models/
COPY data/*.parquet ./data/
COPY data/lancedb_store ./data/lancedb_store
COPY app/ ./app/
COPY run.py .

# Port
EXPOSE 5000

# Start the application with Gunicorn
CMD ["gunicorn", "--workers=1", "--threads=4", "--timeout=120", "--bind=0.0.0.0:5000", "run:app"]