# IV Bot Dockerfile Template with Knowledge Graph Integration
# Based on Wolfi (apko) for minimal, secure container images
# Part of BSW-Arch AI Development Platform

FROM cgr.dev/chainguard/wolfi-base:latest

# Metadata
LABEL maintainer="BSW-Arch Team"
LABEL description="IV Bot with Knowledge Graph Integration"
LABEL org.opencontainers.image.source="https://codeberg.org/IV-Bots"

# Install Python and essential dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-requests \
    py3-aiohttp \
    py3-yaml \
    ca-certificates \
    git

# Create bot user (non-root)
RUN addgroup -g 1000 ivbot && \
    adduser -D -u 1000 -G ivbot ivbot

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy bot utilities from bsw-arch repo
COPY bot-utils/doc_scanner.py /app/utils/
COPY bot-utils/github_api_client.py /app/utils/
COPY bot-utils/create_embeddings_chunks.py /app/utils/

# Copy bot implementation
COPY bot_main.py /app/
COPY config.yaml /app/

# Create directories for knowledge base and cache
RUN mkdir -p /app/data /app/cache /app/logs && \
    chown -R ivbot:ivbot /app

# Switch to non-root user
USER ivbot

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python3 -c "import sys; sys.exit(0)"

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV NEO4J_URI=bolt://neo4j:7687
ENV NEO4J_USER=neo4j
ENV NEO4J_PASSWORD=password
ENV CHROMA_HOST=chromadb
ENV CHROMA_PORT=8000
ENV OLLAMA_HOST=http://ollama:11434

# Entrypoint
ENTRYPOINT ["python3", "bot_main.py"]
