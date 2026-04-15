import asyncio

from temporalio import activity

__all__ = ["send_email"]


@activity.defn
async def send_email(email: str) -> str:
    activity.logger.info(f"Отправка письма на {email}...")
    await asyncio.sleep(2)
    return "Email отправлен"
