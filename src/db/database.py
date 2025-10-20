from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, declared_attr, sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

Base = declarative_base()
DATABASE_URL = 'sqlite+aiosqlite:///data/dbase.db'
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'


async def get_db():
    """Предоставляет асинхронную сессию для работы с базой данных."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
