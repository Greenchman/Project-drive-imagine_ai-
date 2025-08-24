FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (SQLite3 + gcc for some Python packages)
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (make sure .dockerignore excludes env/, __pycache__/ etc.)
COPY . .

#  Run migrations at build time
RUN python manage.py migrate --noinput



# Expose port
EXPOSE 8000

# Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
