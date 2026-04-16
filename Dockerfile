FROM python:3.13-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml ./

FROM base AS test

RUN uv pip install --system -r pyproject.toml --extra test --extra dev

COPY src ./src
COPY tests ./tests

ENV PYTHONPATH="/app/src:$PYTHONPATH"

CMD ["pytest", "-v"]

FROM base AS prod

RUN uv pip install --system -r pyproject.toml

COPY src ./src

ENV PYTHONPATH="/app/src:$PYTHONPATH"

RUN useradd -m appuser && chown -R appuser /app
USER appuser
