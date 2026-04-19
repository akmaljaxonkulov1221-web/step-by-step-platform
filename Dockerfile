FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    libpoppler-cpp-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories for PDF uploads
RUN mkdir -p uploads/pdfs

# Set proper permissions
RUN chmod 755 uploads uploads/pdfs

# Create health check endpoint
RUN echo "from flask import Flask, jsonify\napp = Flask(__name__)\n@app.route('/health')\ndef health():\n    return jsonify({'status': 'healthy', 'timestamp': '2024-04-19'})\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000)" > health_check.py

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
