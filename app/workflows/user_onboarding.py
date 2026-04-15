from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from app.shared.models import UserCreateRequest
from app.activities.user_onboarding import UserActivities


@workflow.defn
class UserOnboardingWorkflow:
    @workflow.run
    async def run(self, request: UserCreateRequest) -> dict:
        workflow.logger.info(f"Начинаем онбординг для {request.name} (ID: {request.user_id})")

        # Шаг 1: Сохранение в Базу Данных
        await workflow.execute_activity(
            UserActivities.create_user_in_db,
            task_queue="cpu-queue",
            args=[request.user_id, request.name, request.email],
            start_to_close_timeout=timedelta(seconds=5)
        )

        # Шаг 2: HTTP запрос в WireMock (с политикой ретраев)
        kyc_status = await workflow.execute_activity(
            UserActivities.call_kyc_api,
            args=[request.user_id, request.name],
            task_queue="io-queue",
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_attempts=3
            )
        )

        # Шаг 3: Обновление статуса в БД
        await workflow.execute_activity(
            UserActivities.update_user_status,
            task_queue="cpu-queue",
            args=[request.user_id, kyc_status],
            start_to_close_timeout=timedelta(seconds=5)
        )

        return {"user_id": request.user_id, "final_status": kyc_status}