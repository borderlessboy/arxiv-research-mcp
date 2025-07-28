# Ultra-lightweight Dockerfile for arXiv Research MCP Server (HTTP, port 8090)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for pdfplumber, PyPDF2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpoppler-cpp-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary code and config for the MCP server
COPY config ./config
COPY scripts/run_server_http.py ./scripts/run_server_http.py
COPY src ./src

# Expose the HTTP port
EXPOSE 8090

# Default command: run the HTTP server on port 8090
CMD ["python", "scripts/run_server_http.py", "--host", "0.0.0.0", "--port", "8090"] 