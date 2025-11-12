# MCP Server Dockerfile
# Uses Chainguard Wolfi Python base for minimal size
# Master Control Plane orchestrator

# ============================================================================
# Stage 1: Builder - Install dependencies
# ============================================================================
FROM cgr.dev/chainguard/python:latest-dev AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM cgr.dev/chainguard/python:latest

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /home/nonroot/.local/lib/python*/site-packages /home/nonroot/.local/lib/python3.12/site-packages

# Copy application source
COPY src/ ./src/

# Copy shared utilities
COPY ../shared/ ./shared/ 2>/dev/null || true

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    LOG_LEVEL=INFO \
    CAG_SERVICE_URL=http://cag-service:8001 \
    RAG_SERVICE_URL=http://rag-service:8002

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run as non-root user (Chainguard default)
USER nonroot

# Start application
CMD ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
