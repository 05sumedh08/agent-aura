# Dockerfile for Agent Aura
# Multi-stage build for production deployment

# ============================================================================
# Stage 1: Base Python image with dependencies
# ============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# ============================================================================
# Stage 2: Dependencies installation
# ============================================================================
FROM base as dependencies

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 3: Production image
# ============================================================================
FROM base as production

# Copy installed dependencies from previous stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Create non-root user
RUN useradd -m -u 1000 agentaura && \
    mkdir -p /app/data /app/output /app/logs && \
    chown -R agentaura:agentaura /app

# Copy application code
COPY --chown=agentaura:agentaura agent_aura/ /app/agent_aura/
COPY --chown=agentaura:agentaura data/ /app/data/

# Switch to non-root user
USER agentaura

# Expose port for ADK Web
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Set entrypoint
ENTRYPOINT ["adk"]

# Default command - run web interface
CMD ["web", "--host", "0.0.0.0", "--port", "8000"]
