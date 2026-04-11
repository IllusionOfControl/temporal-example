import asyncio
from temporalio.client import Client

from app.workflows import GreetingWorkflow

async def main():
    # Подключаемся к серверу
    client = await Client.connect("localhost:7233")

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