from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "get_settings"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    TEMPORAL_URL: str
    DATABASE_URL: str

    MAIN_TASK_QUEUE: str = "main-task-queue"
    CPU_TASK_QUEUE: str = "cpu-task-queue"
    GPU_TASK_QUEUE: str = "gpu-task-queue"
    IO_TASK_QUEUE: str = "io-task-queue"

    VERIFY_KYC_API_URL: str = "http://wiremock:8080/api/v1/verify-kyc"


@lru_cache
def get_settings() -> Settings:
    return Settings()
