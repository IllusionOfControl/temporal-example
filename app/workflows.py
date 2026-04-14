import asyncio
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

from app.models import OrderRequest

with workflow.unsafe.imports_passed_through():
    from app.activities import say_hello, reserve_inventory, charge_payment, generate_invoice, send_email, \
    update_user_status, call_kyc_api, create_user_in_db


@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        workflow.logger.info("Начинаем Workflow")

        # Вызываем активность. Обязательно указываем таймаут!
        result = await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=10)
        )

        return result


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
    async def run(self, order: OrderRequest) -> str:
        workflow.logger.info(f"Начат процесс для заказа {order.order_id}")

        # 1. Резерв товара
        self.status = "Резервирование товара"
        await workflow.execute_activity(
            reserve_inventory, order, start_to_close_timeout=timedelta(seconds=5)
        )

        # 2. Оплата (с настройкой RetryPolicy)
        self.status = "Ожидание оплаты"
        await workflow.execute_activity(
            charge_payment,
            order,
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
            workflow.execute_activity(generate_invoice, order.order_id, start_to_close_timeout=timedelta(seconds=10)),
            workflow.execute_activity(send_email, order.email, start_to_close_timeout=timedelta(seconds=10))
        )

        self.status = "Заказ завершен"
        return f"Успех! Результаты: {results[0]}, {results[1]}"


@workflow.defn
class UserOnboardingWorkflow:
    @workflow.run
    async def run(self, name: str, email: str) -> dict:
        # Получаем ID текущего воркфлоу. Это гениальный способ связать
        # процесс Temporal с записью в БД и обеспечить идемпотентность.
        user_id = workflow.info().workflow_id

        workflow.logger.info(f"Начинаем онбординг для {name} (ID: {user_id})")

        # Шаг 1: Запись в БД
        await workflow.execute_activity(
            create_user_in_db,
            args=[user_id, name, email],
            start_to_close_timeout=timedelta(seconds=5)
        )

        # Шаг 2: HTTP запрос в WireMock (с политикой ретраев)
        kyc_status = await workflow.execute_activity(
            call_kyc_api,
            args=[user_id, name],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_attempts=3  # Если API лежит, пробуем 3 раза
            )
        )

        # Шаг 3: Обновление статуса в БД
        await workflow.execute_activity(
            update_user_status,
            args=[user_id, kyc_status],
            start_to_close_timeout=timedelta(seconds=5)
        )

        return {"user_id": user_id, "final_status": kyc_status}