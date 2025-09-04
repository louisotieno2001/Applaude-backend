# ---- Base Stage ----
# Use a specific version for reproducibility
FROM python:3.11.4-slim-bullseye as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/home/webapp/.local/bin:${PATH}"

# Create a non-root user for security
RUN groupadd -r webapp && useradd --no-log-init -r -g webapp -d /home/webapp -m webapp
USER webapp
WORKDIR /home/webapp/app

# ---- Builder Stage ----
FROM base as builder

# Install build-time dependencies
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev pkg-config
USER webapp

# Copy only the requirements file to leverage Docker cache
COPY --chown=webapp:webapp backend/requirements.txt .

# Install dependencies into a virtual environment
RUN python -m venv /home/webapp/venv
ENV PATH="/home/webapp/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# ---- Final Stage ----
FROM base as final

# Install runtime dependencies
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-libmysqlclient-dev supervisor && \
    rm -rf /var/lib/apt/lists/*
USER webapp

# Copy virtual environment from builder stage
COPY --chown=webapp:webapp --from=builder /home/webapp/venv /home/webapp/venv

# Copy application code
COPY --chown=webapp:webapp backend/ .

# Make the entrypoint script executable inside the container
USER root
RUN chmod +x /home/webapp/app/entrypoint.sh

# Copy supervisor configuration
COPY --chown=root:root backend/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
USER webapp

# Set the entrypoint to run our startup script
ENTRYPOINT ["/home/webapp/app/entrypoint.sh"]
