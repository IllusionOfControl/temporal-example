import asyncio
import logging

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker

from app.activities.greeting import say_hello
from app.infrastructure.logger import setup_logging
from app.settings import Settings, get_settings
from app.workflows.greeting import GreetingWorkflow
from app.workflows.order_processing import OrderProcessingWorkflow
from app.workflows.review_ml import ReviewMLWorkflow
from app.workflows.user_onboarding import UserOnboardingWorkflow

logger = logging.getLogger(__name__)
interrupt_event = asyncio.Event()


async def main():
    settings: Settings = get_settings()
    setup_logging(settings.MAIN_TASK_QUEUE)
    # Подключаемся к локальному серверу
    client = await Client.connect(
        settings.TEMPORAL_URL,
        data_converter=pydantic_data_converter,
    )

    # Создаем воркер
    async with Worker(
        client,
        task_queue=settings.MAIN_TASK_QUEUE,
        workflows=[
            GreetingWorkflow,
            OrderProcessingWorkflow,
            UserOnboardingWorkflow,
            ReviewMLWorkflow,
        ],
        activities=[
            say_hello,
        ],
    ):
        # Wait until interrupted
        logger.info(f"Worker {settings.MAIN_TASK_QUEUE} started, ctrl+c to exit")
        await interrupt_event.wait()
        logger.info("Shutting down")


if __name__ == "__main__":
    asyncio.run(main())
