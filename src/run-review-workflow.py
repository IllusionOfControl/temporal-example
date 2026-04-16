import asyncio
import random
import uuid

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from app.settings import Settings, get_settings
from app.shared.models import ReviewRequest
from app.workflows.review_ml import ReviewMLWorkflow

# Набор тестовых данных
REVIEWS = [
    {
        "text": "Это просто потрясающий сервис! Всё доставили вовремя, товар качественный, упаковка целая. "
        "Я в восторге, буду заказывать еще!",
        "type": "POSITIVE",
    },
    {
        "text": "Какой ужас... Заказал неделю назад, до сих пор не привезли. Поддержка молчит. "
        "Очень плохо, никому не рекомендую этот магазин.",
        "type": "NEGATIVE",
    },
    {
        "text": "Товар нормальный, но доставка подкачала. "
        "Курьер опоздал на два часа и даже не извинился. В целом пользоваться можно, но осадочек остался.",
        "type": "MIXED",
    },
    {
        "text": "Плохо прошиты швы на куртке. Ужас, везде торчат нитки. Оформил возврат. "
        "Надеюсь, деньги вернут быстро.",
        "type": "NEGATIVE",
    },
    {
        "text": "Вчера купил здесь ноутбук. Экран яркий, работает быстро, клавиатура приятная. "
        "Единственный минус - маркий корпус. В остальном всё отлично, спасибо!",
        "type": "POSITIVE",
    },
    {
        "text": "Сервис работает нестабильно. Пытался оформить заказ три раза, постоянно вылетала ошибка. "
        "В итоге купил у конкурентов. Исправьте свой сайт!",
        "type": "NEGATIVE",
    },
]


async def run_test_scenario(client: Client, settings: Settings):
    # Выбираем случайный отзыв
    selected = random.choice(REVIEWS)

    # Генерируем уникальный ID для запуска
    workflow_id = f"review-{uuid.uuid4().hex[:8]}"

    print(f"Запуск Workflow [{workflow_id}]")
    print(f"Текст: {selected['text'][:60]}...")

    request_data = ReviewRequest(text=selected["text"])

    try:
        # Запускаем и ждем результат
        result = await client.execute_workflow(
            ReviewMLWorkflow.run,
            args=[request_data],
            id=workflow_id,
            task_queue=settings.MAIN_TASK_QUEUE,
        )

        print(f"Результат для {workflow_id}:")
        print(f"Тональность: {result['sentiment']}")
        print(f"Summary: {result['summary']}")
        print("-" * 50)

    except Exception as e:
        print(f"Ошибка в Workflow {workflow_id}: {e}")


async def main():
    settings = get_settings()
    client = await Client.connect("localhost:7233", data_converter=pydantic_data_converter)

    # Запустим 3 случайных проверки подряд
    for _ in range(3):
        await run_test_scenario(client, settings)
        # Небольшая пауза между запусками
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
