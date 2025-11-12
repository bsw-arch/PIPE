# CAG Service Dockerfile
# Uses Chainguard Wolfi Python base for minimal size (<50MB target)
# Multi-stage build for optimisation

# ============================================================================
# Stage 1: Builder - Download models and dependencies
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

# Download ML models (sentence-transformers)
RUN python3 -c "from sentence_transformers import SentenceTransformer; \
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); \
    model.save('/models/embeddings')"


# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM cgr.dev/chainguard/python:latest

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /home/nonroot/.local/lib/python*/site-packages /home/nonroot/.local/lib/python3.12/site-packages

# Copy pre-downloaded models
COPY --from=builder /models /models

# Copy application source
COPY src/ ./src/

# Copy shared utilities (if available)
COPY ../shared/ ./shared/ 2>/dev/null || true

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_CACHE_DIR=/models \
    PORT=8001 \
    LOG_LEVEL=INFO

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')"

# Run as non-root user (Chainguard default)
USER nonroot

# Start application
CMD ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
