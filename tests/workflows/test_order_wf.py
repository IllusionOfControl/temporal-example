import asyncio
import uuid

import pytest
from temporalio import activity
from temporalio.worker import Worker

from app.settings import get_settings
from app.shared.models import OrderRequest
from app.workflows.order_processing import OrderProcessingWorkflow


@activity.defn(name="reserve_inventory")
async def mock_reserve_inventory(order: OrderRequest) -> str:
    return "Mocked Reserve"


@activity.defn(name="cancel_inventory_reservation")
async def mock_cancel_inventory(order: OrderRequest) -> str:
    return "Mocked Cancel"


@activity.defn(name="charge_payment")
async def mock_charge_payment(order: OrderRequest) -> str:
    return "Mocked Charge"


@activity.defn(name="generate_invoice")
async def mock_generate_invoice(order_id: str) -> str:
    return "mocked_invoice.pdf"


@activity.defn(name="send_email")
async def mock_send_email(email: str) -> str:
    return "Mocked Email"


@pytest.mark.asyncio
async def test_order_processing_happy_path(temporal_env):
    settings = get_settings()

    worker_main = Worker(
        temporal_env.client,
        task_queue=settings.MAIN_TASK_QUEUE,
        workflows=[OrderProcessingWorkflow],
    )

    worker_io = Worker(
        temporal_env.client,
        task_queue=settings.IO_TASK_QUEUE,
        activities=[mock_reserve_inventory, mock_cancel_inventory, mock_charge_payment, mock_send_email],
    )

    worker_cpu = Worker(
        temporal_env.client,
        task_queue=settings.CPU_TASK_QUEUE,
        activities=[mock_generate_invoice],
    )

    async with worker_main, worker_io, worker_cpu:
        order_data = OrderRequest(
            order_id="TEST-123",
            item_name="Test Item",
            amount=100.0,
            email="test@test.com",
        )

        handle = await temporal_env.client.start_workflow(
            OrderProcessingWorkflow.run,
            order_data,
            id=f"test-order-{uuid.uuid4()}",
            task_queue=settings.MAIN_TASK_QUEUE,
        )

        await asyncio.sleep(0.5)

        status = await handle.query(OrderProcessingWorkflow.get_status)
        assert status == "Ожидание подтверждения менеджера"

        await handle.signal(OrderProcessingWorkflow.approve_order)

        result = await handle.result()

        assert "Успех!" in result
        assert "mocked_invoice.pdf" in result
