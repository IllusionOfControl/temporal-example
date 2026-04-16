import asyncio
from typing import Any

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from temporalio import activity

from app.infrastructure.db import Review
from app.infrastructure.ml_models import TextSummarizerModel

__all__ = ["ReviewActivities"]


class ReviewActivities:
    def __init__(self, session_factory: Any | None = None, summarizer_model: TextSummarizerModel | None = None):
        self.session_factory = session_factory
        self.summarizer = summarizer_model

    @activity.defn
    async def generate_summary(self, text: str) -> str:
        activity.logger.info("Запуск LLM Summarization (GPU)...")

        if self.summarizer is None:
            raise RuntimeError("GPU модель не инициализирована в этом воркере!")

        result = await self.summarizer.predict(text)

        return result

    @activity.defn
    async def save_review(self, review_id: str, text: str) -> str:
        if self.session_factory is None:
            raise RuntimeError("AsyncSessionFactory не инициализирована в этом воркере!")

        activity.logger.info("Сохраняем новый отзыв в БД...")
        async with self.session_factory() as session:
            async with session.begin():
                stmt = insert(Review).values(id=review_id, text=text, status="PROCESSING")
                stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
                await session.execute(stmt)
        return "Saved"

    @activity.defn
    async def analyze_sentiment(self, text: str) -> str:
        activity.logger.info("Запуск Sentiment Analysis (CPU)...")
        await asyncio.sleep(2)
        if "ужас" in text.lower() or "плохо" in text.lower():
            return "NEGATIVE"
        return "POSITIVE"

    @activity.defn
    async def update_results(self, review_id: str, sentiment: str, summary: str) -> str:
        if self.session_factory is None:
            raise RuntimeError("AsyncSessionFactory не инициализирована в этом воркере!")

        activity.logger.info("Сохраняем результаты ML в БД...")
        async with self.session_factory() as session:
            async with session.begin():
                stmt = (
                    update(Review)
                    .where(Review.id == review_id)
                    .values(sentiment=sentiment, summary=summary, status="COMPLETED")
                )
                await session.execute(stmt)
        return "Updated"
