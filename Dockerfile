FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml ./

RUN uv pip install --system -r pyproject.toml

# Копируем весь остальной код
COPY . .

# Добавляем виртуальное окружение в PATH.
# Теперь команды `python` будут автоматически использовать Python из .venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/:$PYTHONPATH"

RUN useradd -m appuser && chown -R appuser /app
USER appuser