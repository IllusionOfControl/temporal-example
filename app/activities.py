import asyncio
import random

import asyncpg
import httpx
from temporalio import activity
from temporalio.exceptions import ApplicationError

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


DB_DSN = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
WIREMOCK_URL = "http://localhost:8080/api/v1/verify-kyc"


@activity.defn
async def create_user_in_db(user_id: str, name: str, email: str) -> str:
    activity.logger.info(f"Сохраняем пользователя {name} в БД...")
    conn = await asyncpg.connect(DB_DSN)
    try:
        # Используем ON CONFLICT для идемпотентности!
        # Если Temporal сделает ретрай, мы не получим ошибку дубликата.
        await conn.execute('''
                           INSERT INTO users (id, name, email, status)
                           VALUES ($1, $2, $3, 'PENDING') ON CONFLICT (id) DO NOTHING
                           ''', user_id, name, email)
    finally:
        await conn.close()
    return "User created"


@activity.defn
async def call_kyc_api(user_id: str, name: str) -> str:
    activity.logger.info(f"Отправляем данные {name} в KYC API...")

    async with httpx.AsyncClient() as client:
        payload = {"user_id": user_id, "name": name}
        response = await client.post(WIREMOCK_URL, json=payload)
        if response.status_code >= 500:
            # Temporal автоматически будет ретраить ApplicationError
            raise ApplicationError("KYC API is down", type="HttpError")

        data = response.json()
        activity.logger.info(f"Ответ от API: {data}")
        return data["status"]  # Вернет "VERIFIED" из нашего мока


@activity.defn
async def update_user_status(user_id: str, status: str) -> str:
    activity.logger.info(f"Обновляем статус пользователя {user_id} на {status}...")
    conn = await asyncpg.connect(DB_DSN)
    try:
        await conn.execute('UPDATE users SET status = $1 WHERE id = $2', status, user_id)
    finally:
        await conn.close()
    return f"Status updated to {status}"
