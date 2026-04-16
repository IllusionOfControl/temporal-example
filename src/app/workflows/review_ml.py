from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.activities.review_ml import ReviewActivities
    from app.settings import get_settings
    from app.shared.models import ReviewRequest

__all__ = ["ReviewMLWorkflow"]


@workflow.defn
class ReviewMLWorkflow:
    @workflow.run
    async def run(self, request: dict) -> dict:
        settings = get_settings()

        # 1. Валидация входящих данных через Pydantic
        review = ReviewRequest.model_validate(request)
        review_id = workflow.info().workflow_id

        workflow.logger.info(f"Начат анализ отзыва {review_id}")

        # 2. Сохранение в БД (Default Queue)
        await workflow.execute_activity(
            ReviewActivities.save_review,
            args=[review_id, review.text],
            task_queue=settings.IO_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=5),
        )

        # 3. Легкий ML (Default Queue)
        sentiment = await workflow.execute_activity(
            ReviewActivities.analyze_sentiment,
            args=[review.text],
            task_queue=settings.CPU_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=10),
        )

        # 4. Тяжелый ML (GPU Queue)
        summary = await workflow.execute_activity(
            ReviewActivities.generate_summary,
            args=[review.text],
            task_queue=settings.GPU_TASK_QUEUE,
            start_to_close_timeout=timedelta(minutes=5),
            heartbeat_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=5), maximum_attempts=3),
        )

        # 5. Обновление БД (Default Queue)
        await workflow.execute_activity(
            ReviewActivities.update_results,
            args=[review_id, sentiment, summary],
            task_queue=settings.IO_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=5),
        )

        return {"sentiment": sentiment, "summary": summary}
