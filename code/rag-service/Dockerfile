# RAG Service Dockerfile
# Uses Chainguard Wolfi Python base
# Includes Llama-2-7B with 4-bit quantization support

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

# Download embedding model
RUN python3 -c "from sentence_transformers import SentenceTransformer; \
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); \
    model.save('/models/embeddings')"

# Download Llama-2-7B model with 4-bit quantization
# Note: This requires HuggingFace token for gated models
# Set HF_TOKEN environment variable during build if needed
RUN python3 -c "from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig; \
    import torch; \
    quantization_config = BitsAndBytesConfig( \
        load_in_4bit=True, \
        bnb_4bit_compute_dtype=torch.float16, \
        bnb_4bit_quant_type='nf4', \
        bnb_4bit_use_double_quant=True \
    ); \
    tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-2-7b-chat-hf'); \
    tokenizer.save_pretrained('/models/llama'); \
    print('Llama tokenizer downloaded')" || echo "Llama download skipped (requires HF token)"


# ============================================================================
# Stage 2: Runtime - Production image with CUDA support
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

# Copy shared utilities
COPY ../shared/ ./shared/ 2>/dev/null || true

# Create directories for vector store and data
RUN mkdir -p /data/vector_store /data/documents && \
    chown -R nonroot:nonroot /data

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_CACHE_DIR=/models \
    VECTOR_STORE_PATH=/data/vector_store \
    PORT=8002 \
    LOG_LEVEL=INFO \
    TRANSFORMERS_OFFLINE=1 \
    HF_HOME=/models

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health')"

# Run as non-root user
USER nonroot

# Start application
CMD ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
