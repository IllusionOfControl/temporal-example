import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from app.activities import say_hello, reserve_inventory, charge_payment, generate_invoice, send_email
from app.workflows import GreetingWorkflow, OrderProcessingWorkflow

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")


async def main():
    # Подключаемся к локальному серверу
    client = await Client.connect(TEMPORAL_HOST)

    # Создаем воркер
    worker = Worker(
        client,
        task_queue="default",
        workflows=[
            GreetingWorkflow,
            OrderProcessingWorkflow
        ],
        activities=[
            say_hello,
            reserve_inventory,
            charge_payment,
            generate_invoice,
            send_email
        ],
    )

    print("Воркер запущен. Нажми Ctrl+C для остановки.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
