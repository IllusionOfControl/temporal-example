import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from app.activities.email import send_email

with workflow.unsafe.imports_passed_through():
    from app.settings import Settings, get_settings
    from app.activities.order_processing import OrderActivities
    from app.shared.models import OrderRequest

__all__ = ["OrderProcessingWorkflow"]


@workflow.defn
class OrderProcessingWorkflow:
    def __init__(self) -> None:
        self.status = "Инициализация"
        self.manager_approved = False

    # QUERY: Позволяет узнать текущий статус извне
    @workflow.query
    def get_status(self) -> str:
        return self.status

    # SIGNAL: Позволяет пнуть Workflow извне
    @workflow.signal
    def approve_order(self) -> None:
        self.manager_approved = True
        self.status = "Одобрено менеджером"

    @workflow.run
    async def run(self, order: OrderRequest, settings: Settings = get_settings()) -> str:
        workflow.logger.info(f"Начат процесс для заказа {order.order_id}")

        # 1. Резерв товара
        self.status = "Резервирование товара"
        await workflow.execute_activity(
            OrderActivities.reserve_inventory,
            order,
            task_queue=settings.IO_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=5)
        )

        # 2. Оплата (с настройкой RetryPolicy)
        self.status = "Ожидание оплаты"
        await workflow.execute_activity(
            OrderActivities.charge_payment,
            order,
            task_queue=settings.IO_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=5),
            # Настраиваем повторные попытки: максимум 5 попыток, пауза 2 секунды
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_attempts=5
            )
        )

        # 3. Ожидание сигнала от менеджера
        self.status = "Ожидание подтверждения менеджера"
        workflow.logger.info("Workflow заснул и ждет сигнала approve_order...")

        # Workflow приостанавливается здесь. Он может ждать секунды, дни или месяцы!
        await workflow.wait_condition(lambda: self.manager_approved)

        # 4. Параллельное выполнение (Чек + Email)
        self.status = "Сборка документов и отправка"
        workflow.logger.info("Менеджер подтвердил. Запускаем параллельные задачи.")

        # Запускаем активности одновременно
        results = await asyncio.gather(
            workflow.execute_activity(
                OrderActivities.generate_invoice,
                order.order_id,
                task_queue=settings.CPU_TASK_QUEUE,
                start_to_close_timeout=timedelta(seconds=10)
            ),
            workflow.execute_activity(
                send_email,
                order.email,
                task_queue=settings.IO_TASK_QUEUE,
                start_to_close_timeout=timedelta(seconds=10)
            )
        )

        self.status = "Заказ завершен"
        return f"Успех! Результаты: {results[0]}, {results[1]}"
