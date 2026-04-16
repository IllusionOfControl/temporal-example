# tests/activities/test_greeting.py
import pytest
from temporalio.testing import ActivityEnvironment

from app.activities.greeting import say_hello


@pytest.mark.asyncio
async def test_say_hello_activity():
    # Создаем изолированное окружение для активности
    env = ActivityEnvironment()

    # Запускаем активность
    result = await env.run(say_hello, "Иван")

    # Проверяем результат
    assert result == "Привет, Иван! Добро пожаловать в Temporal."
