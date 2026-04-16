FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads

# Run data restoration
RUN python restore_full_previous_state.py

# Create health check endpoint
RUN echo "from flask import Flask, jsonify\napp = Flask(__name__)\n@app.route('/health')\ndef health():\n    return jsonify({'status': 'healthy', 'timestamp': '2024-04-16'})\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000)" > health_check.py

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
