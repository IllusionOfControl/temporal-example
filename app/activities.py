import asyncio
import random
from temporalio import activity
from app.models import OrderRequest


@activity.defn
async def say_hello(name: str) -> str:
    # Здесь может быть любая логика: запросы к API, БД и т.д.
    activity.logger.info(f"Выполняем активность для: {name}")
    return f"Привет, {name}! Добро пожаловать в Temporal."


@activity.defn
async def reserve_inventory(order: OrderRequest) -> str:
    activity.logger.info(f"Резервируем товар {order.item_name} для заказа {order.order_id}")
    await asyncio.sleep(1)  # Имитация работы
    return "Товар зарезервирован"


@activity.defn
async def charge_payment(order: OrderRequest) -> str:
    activity.logger.info(f"Попытка списать ${order.amount}...")
    await asyncio.sleep(1)

    # Имитируем нестабильное API банка (падает в 50% случаев)
    if random.random() < 0.5:
        activity.logger.error("ОШИБКА БАНКА! Платеж не прошел.")
        raise Exception("Bank API timeout or error")

    activity.logger.info("Оплата успешно прошла!")
    return "Оплата получена"


@activity.defn
async def generate_invoice(order_id: str) -> str:
    activity.logger.info(f"Генерация PDF чека для {order_id}...")
    await asyncio.sleep(2)
    return f"invoice_{order_id}.pdf"


@activity.defn
async def send_email(email: str) -> str:
    activity.logger.info(f"Отправка письма на {email}...")
    await asyncio.sleep(2)
    return "Email отправлен"
