from temporalio import activity
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import update
from app.infrastructure.db import User
from app.infrastructure.kyc_client import KYCClient


class UserActivities:
    def __init__(self, session_factory, kyc_client: KYCClient):
        self.session_factory = session_factory
        self.kyc_client = kyc_client

    @activity.defn
    async def create_user_in_db(self, user_id: str, name: str, email: str) -> str:
        activity.logger.info(f"Сохраняем пользователя {name} в БД...")

        async with self.session_factory() as session:
            async with session.begin():
                # SQLAlchemy версия ON CONFLICT DO NOTHING
                stmt = insert(User).values(
                    id=user_id, name=name, email=email, status='PENDING'
                ).on_conflict_do_nothing(index_elements=['id'])

                await session.execute(stmt)
            # commit произойдет автоматически при выходе из context manager 'begin'

        return "User created or already exists"

    @activity.defn
    async def call_kyc_api(self, user_id: str, name: str) -> str:
        activity.logger.info(f"Отправляем данные {name} в KYC API...")
        return await self.kyc_client.verify_kyc(user_id, name)

    @activity.defn
    async def update_user_status(self, user_id: str, status: str) -> str:
        activity.logger.info(f"Обновляем статус пользователя {user_id} на {status}...")

        async with self.session_factory() as session:
            async with session.begin():
                stmt = update(User).where(User.id == user_id).values(status=status)
                await session.execute(stmt)

        return f"Status updated to {status}"