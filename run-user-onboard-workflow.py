import asyncio
import uuid

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from app.settings import get_settings
from app.shared.models import UserCreateRequest
from app.workflows.user_onboarding import UserOnboardingWorkflow


async def main():
    settings = get_settings()
    client = await Client.connect(
        "localhost:7233",
        data_converter=pydantic_data_converter
    )

    # Генерируем уникальный ID для пользователя (он же будет ID процесса)
    user_create_request = UserCreateRequest(
        user_id=str(uuid.uuid4().hex[:8]),
        name="Иван Иванов",
        email="ivan@example.com",
    )

    process_id = f"user-{user_create_request.user_id}"

    print(f"Запускаем процесс онбординга: {process_id}")
    result = await client.execute_workflow(
        UserOnboardingWorkflow.run,
        user_create_request,
        id=process_id,
        task_queue=settings.MAIN_TASK_QUEUE,
    )

    print(f"Результат: {result}")


if __name__ == "__main__":
    asyncio.run(main())
