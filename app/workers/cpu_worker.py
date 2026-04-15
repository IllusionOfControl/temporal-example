import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from app.activities.greeting import say_hello
from app.activities.order_processing import OrderActivities
from app.settings import get_settings, Settings


async def main(settings: Settings = get_settings()):
    # Подключаемся к локальному серверу
    client = await Client.connect(settings.TEMPORAL_URL)

    order_acts = OrderActivities()

    # Создаем воркер
    worker = Worker(
        client,
        task_queue=settings.CPU_TASK_QUEUE,
        activities=[
            say_hello,
            order_acts.generate_invoice,
        ]
    )

    print(f"Воркер {settings.CPU_TASK_QUEUE} запущен. Нажми Ctrl+C для остановки.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
