import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from app.activities.greeting import say_hello
from app.settings import get_settings, Settings
from app.workflows.greeting import GreetingWorkflow
from app.workflows.order_processing import OrderProcessingWorkflow
from app.workflows.user_onboarding import UserOnboardingWorkflow


async def main(settings: Settings = get_settings()):
    # Подключаемся к локальному серверу
    client = await Client.connect(settings.TEMPORAL_URL)

    # Создаем воркер
    worker = Worker(
        client,
        task_queue=settings.MAIN_TASK_QUEUE,
        workflows=[
            GreetingWorkflow,
            OrderProcessingWorkflow,
            UserOnboardingWorkflow,
        ],
        activities=[
            say_hello,
        ]
    )

    print(f"Воркер {settings.MAIN_TASK_QUEUE} запущен. Нажми Ctrl+C для остановки.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
