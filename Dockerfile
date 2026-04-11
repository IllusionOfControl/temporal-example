# 1. Use the official uv image to provide the binary
FROM ghcr.io/astral-sh/uv:latest AS uv_bin

# 2. Use Python 3.14
FROM python:3.14-slim

# Install the uv binary
COPY --from=uv_bin /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation and prevent uv from creating a virtualenv
# inside the container (installing to system Python is standard for Docker)
ENV UV_COMPILE_BYTECODE=1
ENV UV_SYSTEM_PYTHON=1

# Copy only the files needed for dependency installation
# This allows Docker to cache the 'uv sync' layer
COPY pyproject.toml uv.lock ./

# Install dependencies
# --no-install-project tells uv not to install the local package yet (just deps)
# --frozen ensures uv.lock isn't updated during the build
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY . .

# Install the project itself (if it's defined as a package in pyproject.toml)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Run the application
CMD ["python", "worker.py"]