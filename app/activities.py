from temporalio import activity

@activity.defn
async def say_hello(name: str) -> str:
    # Здесь может быть любая логика: запросы к API, БД и т.д.
    activity.logger.info(f"Выполняем активность для: {name}")
    return f"Привет, {name}! Добро пожаловать в Temporal."