# Используем легковесный образ Python
FROM python:3.14-slim

# Копируем бинарник uv из официального образа (самый быстрый и надежный способ)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Устанавливаем рабочую директорию
WORKDIR /app

# Настройки uv для оптимизации в Docker
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Сначала копируем только файлы зависимостей для кэширования слоев Docker
COPY pyproject.toml ./
# Если локально сгенерируешь uv.lock, раскомментируй строку ниже:
# COPY uv.lock ./

# Устанавливаем зависимости.
# uv автоматически создаст виртуальное окружение в папке /app/.venv
RUN uv sync --no-install-project

# Копируем весь остальной код
COPY . .

# Добавляем виртуальное окружение в PATH.
# Теперь команды `python` будут автоматически использовать Python из .venv
ENV PATH="/app/.venv/bin:$PATH"

# Запускаем воркер
CMD ["python", "app/worker.py"]