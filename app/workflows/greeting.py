from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from app.activities.greeting import say_hello

__all__ = ["GreetingWorkflow"]


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
