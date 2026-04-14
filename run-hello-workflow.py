import asyncio
import os

from temporalio.client import Client

from app.workflows import GreetingWorkflow

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")

async def main():
    # Подключаемся к серверу
    client = await Client.connect("26.5.2.110:7233")

    # Запускаем Workflow и ждем результат
    result = await client.execute_workflow(
        GreetingWorkflow.run,
        args=("Разработчик",), # Аргумент для Workflow
        id="hello-workflow-1", # Уникальный ID запуска
        task_queue="hello-task-queue",
    )

    print(f"Результат Workflow: {result}")

if __name__ == "__main__":
    asyncio.run(main())