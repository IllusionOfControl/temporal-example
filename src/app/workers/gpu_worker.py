import asyncio

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker

from app.activities.review_ml import ReviewActivities
from app.infrastructure.ml_models import TextSummarizerModel
from app.settings import get_settings, Settings

interrupt_event = asyncio.Event()


async def main(settings: Settings = get_settings()):
    # Подключаемся к локальному серверу
    client = await Client.connect(
        settings.TEMPORAL_URL,
        data_converter=pydantic_data_converter,
    )

    model = TextSummarizerModel()

    review_acts = ReviewActivities(summarizer_model=model)

    # Создаем воркер
    async with Worker(
            client,
            task_queue=settings.GPU_TASK_QUEUE,
            activities=[
                review_acts.generate_summary,
            ]
    ):
        # Wait until interrupted
        print(f"Worker {settings.GPU_TASK_QUEUE} started, ctrl+c to exit")
        await interrupt_event.wait()
        print("Shutting down")


if __name__ == "__main__":
    asyncio.run(main())
