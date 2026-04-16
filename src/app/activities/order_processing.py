import asyncio
import random

from temporalio import activity

from app.shared.models import OrderRequest

__all__ = ["OrderActivities"]


class OrderActivities:
    @activity.defn
    async def reserve_inventory(self, order: OrderRequest) -> str:
        activity.logger.info(f"Резервируем товар {order.item_name} для заказа {order.order_id}")
        await asyncio.sleep(1)  # Имитация работы
        return "Товар зарезервирован"

    @activity.defn
    async def cancel_inventory_reservation(self, order: OrderRequest) -> str:
        activity.logger.warning(f"SAGA: Отмена резерва товара {order.item_name} для заказа {order.order_id}")
        await asyncio.sleep(1)
        return "Резерв отменен"

    @activity.defn
    async def charge_payment(self, order: OrderRequest) -> str:
        activity.logger.info(f"Попытка списать ${order.amount}...")
        await asyncio.sleep(1)

        # Имитируем нестабильное API банка (падает в 50% случаев)
        if random.random() < 0.5:
            activity.logger.error("ОШИБКА БАНКА! Платеж не прошел.")
            raise Exception("Bank API timeout or error")

        activity.logger.info("Оплата успешно прошла!")
        return "Оплата получена"

    @activity.defn
    async def generate_invoice(self, order_id: str) -> str:
        activity.logger.info(f"Генерация PDF чека для {order_id}...")
        await asyncio.sleep(2)
        return f"invoice_{order_id}.pdf"
