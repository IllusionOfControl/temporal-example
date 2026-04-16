import asyncio
import logging

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker

from app.activities.greeting import say_hello
from app.activities.order_processing import OrderActivities
from app.activities.review_ml import ReviewActivities
from app.infrastructure.logger import setup_logging
from app.settings import get_settings, Settings

logger = logging.getLogger(__name__)
interrupt_event = asyncio.Event()


async def main(settings: Settings = get_settings()):
    setup_logging(settings.MAIN_TASK_QUEUE)
    # Подключаемся к локальному серверу
    client = await Client.connect(
        settings.TEMPORAL_URL,
        data_converter=pydantic_data_converter,
    )

    order_acts = OrderActivities()
    review_acts = ReviewActivities()

    # Создаем воркер
    async with Worker(
            client,
            task_queue=settings.CPU_TASK_QUEUE,
            activities=[
                say_hello,
                order_acts.generate_invoice,
                review_acts.analyze_sentiment
            ]
    ):
        # Wait until interrupted
        logger.info(f"Worker {settings.MAIN_TASK_QUEUE} started, ctrl+c to exit")
        await interrupt_event.wait()
        logger.info("Shutting down")


if __name__ == "__main__":
    asyncio.run(main())
