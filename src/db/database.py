from datetime import datetime

from sqlalchemy import func, create_engine
from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

#Base = declarative_base()
DATABASE_URL = 'sqlite:///data/dbase.db'
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class BaseModel(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'


def get_db():
    """Предоставляет асинхронную сессию для работы с базой данных."""
    with SessionLocal() as session:
        try:
            yield session
        finally:
            session.close()
