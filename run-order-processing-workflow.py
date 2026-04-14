import asyncio
from temporalio.client import Client
from app.models import OrderRequest
from app.workflows import OrderProcessingWorkflow

async def main():
    client = await Client.connect("26.5.2.110:7233")

    order = OrderRequest(
        order_id="ORDER-777",
        item_name="Ноутбук",
        amount=1500.00,
        email="customer@example.com"
    )

    print("1. Запускаем Workflow...")
    handle = await client.start_workflow(
        OrderProcessingWorkflow.run,
        args=(order,),
        id=f"workflow-{order.order_id}",
        task_queue="order-task-queue",
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