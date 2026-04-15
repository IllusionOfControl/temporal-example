from temporalio import activity


@activity.defn
async def say_hello(name: str) -> str:
    activity.logger.info(f"Выполняем активность для: {name}")
    return f"Привет, {name}! Добро пожаловать в Temporal."
