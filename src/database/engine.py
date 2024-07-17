"""Файл с функциями для запуска базы данных"""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from src.config.config import Config
from src.database.models import Base

engine = create_async_engine(Config.db_url, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_db():
    '''Создание таблиц базы данных'''

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    '''Удаление таблиц базы данных'''

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)