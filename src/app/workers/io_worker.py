import asyncio
import logging

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker

from app.activities.email import send_email
from app.activities.order_processing import OrderActivities
from app.activities.review_ml import ReviewActivities
from app.activities.user_onboarding import UserActivities
from app.infrastructure.db import get_session_factory
from app.infrastructure.kyc_client import KYCClient
from app.infrastructure.logger import setup_logging
from app.settings import Settings, get_settings

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

    # Создаём зависимости
    session_factory = get_session_factory(settings.DATABASE_URL)
    kyc_client = KYCClient(settings.VERIFY_KYC_API_URL)

    # Создаём активности с зависимостями
    user_acts = UserActivities(session_factory, kyc_client)
    order_acts = OrderActivities()
    review_acts = ReviewActivities(session_factory)

    # Создаем воркер
    async with Worker(
        client,
        task_queue=settings.IO_TASK_QUEUE,
        activities=[
            send_email,
            order_acts.charge_payment,
            order_acts.reserve_inventory,
            order_acts.cancel_inventory_reservation,
            user_acts.create_user_in_db,
            user_acts.call_kyc_api,
            user_acts.update_user_status,
            review_acts.save_review,
            review_acts.update_results,
        ],
    ):
        # Wait until interrupted
        logger.info(f"Worker {settings.MAIN_TASK_QUEUE} started, ctrl+c to exit")
        await interrupt_event.wait()
        logger.info("Shutting down")


if __name__ == "__main__":
    asyncio.run(main())
