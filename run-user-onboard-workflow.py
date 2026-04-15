import asyncio
import uuid
from temporalio.client import Client
from app.workflows.user_onboarding import UserOnboardingWorkflow

async def main():
    client = await Client.connect("localhost:7233")

    # Генерируем уникальный ID для процесса (он же будет ID в базе)
    process_id = f"user-{uuid.uuid4().hex[:8]}"

    print(f"Запускаем процесс онбординга: {process_id}")
    result = await client.execute_workflow(
        UserOnboardingWorkflow.run,
        args=["Иван Иванов", "ivan@example.com"],
        id=process_id,
        task_queue="default",
    )

    print(f"Результат: {result}")

if __name__ == "__main__":
    asyncio.run(main())