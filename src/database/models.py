"""Файл с моделями базы данных"""

from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, declarative_base

Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger)
    chat_on: Mapped[bool] = mapped_column(Boolean())


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String())
    executor: Mapped[str] = mapped_column(String(20), nullable=True)
    deadline: Mapped[str] = mapped_column(DateTime(), nullable=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'))




