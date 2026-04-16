import asyncio
import uuid

from temporalio.client import Client

from app.settings import get_settings
from app.workflows.greeting import GreetingWorkflow

async def main():
    settings = get_settings()
    # Подключаемся к серверу
    client = await Client.connect("localhost:7233")

    # Запускаем Workflow и ждем результат
    result = await client.execute_workflow(
        GreetingWorkflow.run,
        args=("Разработчик",), # Аргумент для Workflow
        id=f"hello-workflow-{uuid.uuid4()}", # Уникальный ID запуска
        task_queue=settings.MAIN_TASK_QUEUE,
    )

    print(f"Результат Workflow: {result}")

if __name__ == "__main__":
    asyncio.run(main())
