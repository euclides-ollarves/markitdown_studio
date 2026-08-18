FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for document handling and audio
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "run_gui.py", "--host", "0.0.0.0", "--port", "8000", "--no-browser"]
