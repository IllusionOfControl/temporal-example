import asyncio

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker

from app.activities.greeting import say_hello
from app.activities.order_processing import OrderActivities
from app.settings import get_settings, Settings

interrupt_event = asyncio.Event()


async def main(settings: Settings = get_settings()):
    # Подключаемся к локальному серверу
    client = await Client.connect(
        settings.TEMPORAL_URL,
        data_converter=pydantic_data_converter,
    )

    order_acts = OrderActivities()

    # Создаем воркер
    async with Worker(
            client,
            task_queue=settings.CPU_TASK_QUEUE,
            activities=[
                say_hello,
                order_acts.generate_invoice,
            ]
    ):
        # Wait until interrupted
        print(f"Worker {settings.CPU_TASK_QUEUE} started, ctrl+c to exit")
        await interrupt_event.wait()
        print("Shutting down")


if __name__ == "__main__":
    asyncio.run(main())
