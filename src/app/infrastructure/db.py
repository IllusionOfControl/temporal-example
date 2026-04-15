from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    status: Mapped[str]


def get_session_factory(dsn: str):
    engine = create_async_engine(dsn, pool_size=20, max_overflow=10)
    return async_sessionmaker(bind=engine, expire_on_commit=False)
