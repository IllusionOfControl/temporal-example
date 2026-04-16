import asyncio
import uuid

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from app.settings import get_settings
from app.shared.models import OrderRequest
from app.workflows.order_processing import OrderProcessingWorkflow

async def main():
    settings = get_settings()
    client = await Client.connect(
        "localhost:7233",
        data_converter=pydantic_data_converter,
    )

    order = OrderRequest(
        order_id="ORDER-777",
        item_name="Ноутбук",
        amount=1500.00,
        email="customer@example.com"
    )

    print("1. Запускаем Workflow...")
    handle = await client.start_workflow(
        OrderProcessingWorkflow.run,
        order,
        id=f"workflow-{uuid.uuid4()}",
        task_queue=settings.MAIN_TASK_QUEUE,
    )

    # Ждем пару секунд, чтобы прошли первые активности
    await asyncio.sleep(3)

    print("\n2. Запрашиваем текущий статус (Query)...")
    status = await handle.query(OrderProcessingWorkflow.get_status)
    print(f"   Текущий статус: {status}")

    print("\n3. Ждем 5 секунд (имитация работы менеджера)...")
    await asyncio.sleep(5)

    print("\n4. Отправляем сигнал подтверждения (Signal)...")
    await handle.signal(OrderProcessingWorkflow.approve_order)

    print("\n5. Ждем завершения Workflow...")
    result = await handle.result()
    print(f"\nИТОГ: {result}")

if __name__ == "__main__":
    asyncio.run(main())