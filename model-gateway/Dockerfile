FROM python:3.12-slim-bookworm

WORKDIR /app

ENV POETRY_VERSION=2.0.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

# Install system dependencies and poetry
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 -

# Copy dependency files
COPY poetry.lock pyproject.toml /app/

# Install dependencies
RUN poetry install --no-root

# Copy application code
COPY . /app

# Copy entrypoint script and set permissions
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Create non-root user and set permissions
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --group appgroup \
    && chown -R appgroup:appgroup /app

# Switch to non-root user
USER appgroup

# Expose the port
EXPOSE 4460

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PORT=4460

ENTRYPOINT ["/app/entrypoint.sh"]