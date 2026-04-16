import pytest
import uuid
from temporalio.worker import Worker
from app.workflows.greeting import GreetingWorkflow
from app.activities.greeting import say_hello

@pytest.mark.asyncio
async def test_greeting_workflow(temporal_env):
    task_queue = f"test-queue-{uuid.uuid4()}"

    async with Worker(
        temporal_env.client,
        task_queue=task_queue,
        workflows=[GreetingWorkflow],
        activities=[say_hello],
    ):
        result = await temporal_env.client.execute_workflow(
            GreetingWorkflow.run,
            "Тест",
            id=f"test-wf-{uuid.uuid4()}",
            task_queue=task_queue,
        )

        assert result == "Привет, Тест! Добро пожаловать в Temporal."