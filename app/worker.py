import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from app.activities import say_hello
from app.workflows import GreetingWorkflow


async def main():
    # Подключаемся к локальному серверу
    client = await Client.connect("localhost:7233")

    # Создаем воркер
    worker = Worker(
        client,
        task_queue="hello-task-queue",
        workflows=[GreetingWorkflow],
        activities=[say_hello],
    )

    print("Воркер запущен. Нажми Ctrl+C для остановки.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())