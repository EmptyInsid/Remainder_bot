"""Файл с запросами к базе данных"""

from sqlalchemy import select, Sequence, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Chat, Task
from src.exceptions.myExeptions import *


async def set_chat(chat_id: int, session: AsyncSession) -> None:
    '''
    Добавление нового чата в таблицу после включения бота в чате (команда /bot_on)

    :param chat_id: id чата для добавления
    :param session: сессия бд бота
    '''

    chat = await session.scalar(select(Chat).where(Chat.chat_id == chat_id))

    if not chat:
        session.add(Chat(chat_id=chat_id,
                         chat_on=False))
        await session.commit()


async def set_chat_on(chat_id: int, session: AsyncSession) -> None:
    '''
    Добавление нового чата в таблицу после включения бота в чате (команда /bot_on)

    :param chat_id: id чата для добавления
    :param session: сессия бд бота
    '''

    chat = await session.scalar(select(Chat).where(Chat.chat_id == chat_id))

    if chat:
        chat.chat_on = True
        await session.commit()
    else:
        raise NoneChatException


async def set_chat_off(chat_id: int, session: AsyncSession) -> None:
    '''
    Добавление нового чата в таблицу после включения бота в чате (команда /bot_on)

    :param chat_id: id чата для добавления
    :param session: сессия бд бота
    '''

    chat = await session.scalar(select(Chat).where(Chat.chat_id == chat_id))

    if chat:
        chat.chat_on = False
        await session.commit()
    else:
        raise NoneChatException


async def set_task(chat_id: int, task: dict, session: AsyncSession) -> Task:
    '''
    Добавление задачи в таблицу (ответственный, задача, дедлайн)

    :param chat_id: телеграм id чата, к которому относится данная задача
    :param task: словарь с данными о задаче (ответственный, задача, дедлайн)
    :param session: сессия бд бота
    :return id добавленной задачи
    '''
    try:
        chat_id_db = await get_chat_id(chat_id, session)

        task_db = insert(Task).values(description=task["description"],
                                      executor=task["executor"],
                                      deadline=task["deadline"],
                                      chat_id=chat_id_db
                                      ).returning(Task)
        result = await session.execute(task_db)
        new = result.scalar_one()
        await session.commit()
        return new

    except NoneChatException:
        raise


async def get_chat_id(chat_id: int, session: AsyncSession) -> int:
    '''
    Получение id, под которым данный чат сохранён в базу данных

    :param chat_id: телеграм id чата
    :param session: сессия бд бота
    :return: id, под которым данный чат сохранён в базу данных
    '''

    chat = await session.scalar(select(Chat)
                                .where(Chat.chat_id == chat_id))

    if chat:
        return chat.id
    else:
        raise NoneChatException


async def get_is_chat_on(chat_id: int, session: AsyncSession) -> bool:
    '''
    Включен ли чат для уведомления ботом

    :param chat_id: id чата, у которого проверяем
    :return: включен ли чат (True or False)
    '''

    chat = await session.scalar(select(Chat)
                                .where(Chat.chat_id == chat_id))

    if chat:
        return chat.chat_on
    else:
        raise NoneChatException


async def get_task(chat_id: int, task_description: str, session: AsyncSession) -> Task:
    '''
    Получение задачи из таблицы базы данных по id задачи и id чата

    :param task_description: задача
    :param chat_id: телеграм id чата
    :param session: сессия бд бота
    :return:
    '''

    try:
        chat_id_db = await get_chat_id(chat_id, session)
        task = await session.scalar(
            select(Task)
            .where(Task.chat_id == chat_id_db,
                   Task.description == task_description))
        if task:
            return task
        else:
            raise NoneTaskException

    except (NoneChatException, NoneTaskException):
        raise


async def get_task_by_id(chat_id: int, task_id: int, session: AsyncSession) -> Task:
    '''
    Получение задачи из таблицы базы данных по id задачи и id чата

    :param task_id: задача
    :param chat_id: телеграм id чата
    :param session: сессия бд бота
    :return:
    '''

    try:
        chat_id_db = await get_chat_id(chat_id, session)
        task = await session.scalar(
            select(Task)
            .where(Task.chat_id == chat_id_db,
                   Task.id == task_id))
        if task:
            return task
        else:
            raise NoneTaskException

    except (NoneChatException, NoneTaskException):
        raise


async def get_all_tasks(chat_id: int, session: AsyncSession) -> Sequence[Task]:
    '''
    Получение всех задач для данного чата

    :param chat_id: телеграм id чата
    :param session: сессия бд бота
    :return: пул задач данного чата
    '''

    try:
        chat_id_db = await get_chat_id(chat_id, session)
        result = await session.execute(select(Task)
                                       .where(Task.chat_id == chat_id_db))
        tasks = result.scalars().all()

        return tasks

    except NoneChatException:
        raise


async def get_overdue_tasks(chat_id: int, session: AsyncSession) -> Sequence[Task]:
    '''
    Получение всех прочроченных задач для данного чата

    :param chat_id: телеграм id чата
    :param session: сессия бд бота
    :return: пул просроченных задач данного чата
    '''

    try:
        now = datetime.now()
        chat_id_db = await get_chat_id(chat_id, session)
        result = await session.execute(select(Task)
                                       .where(Task.chat_id == chat_id_db,
                                              Task.deadline <= now))
        tasks = result.scalars().all()

        return tasks
    except NoneChatException:
        raise


async def delete_task(chat_id: int, task_id: int, session: AsyncSession) -> None:
    '''
    Удаление задачи по её id

    :param chat_id: телеграм id чата
    :param task_id: id задачи
    :param session: сессия бд бота
    '''

    try:
        chat_id_db = await get_chat_id(chat_id, session)
        task = await session.scalar(select(Task)
                                    .where(Task.chat_id == chat_id_db,
                                           Task.id == task_id))

        if task:
            await session.delete(task)
            await session.commit()
        else:
            raise NoneTaskException

    except (NoneChatException, NoneTaskException):
        raise


async def change_task_time(chat_id: int, task_id: int, task_new_time: datetime, session: AsyncSession) -> None:
    '''
    Изменение дедлайна для задачи в таблице по id задачи и телеграм id чата

    :param chat_id: телеграм id чата
    :param task_id: id задачи
    :param task_new_time: новое время для задачи
    :param session: сессия бд бота
    '''
    try:

        chat_id_db = await get_chat_id(chat_id, session)
        task = await session.scalar(select(Task)
                                    .where(Task.chat_id == chat_id_db,
                                           Task.id == task_id))

        if task:
            task.deadline = task_new_time
            await session.commit()
        else:
            raise NoneTaskException

    except (NoneChatException, NoneTaskException):
        raise


async def delete_all_tasks(chat_id: int, session: AsyncSession) -> None:
    '''
    Удаление всех задач чата

    :param chat_id: телеграм id чата
    :param session: сессия бд бота
    '''
    try:
        chat_id_db = await get_chat_id(chat_id, session)
        tasks = await session.scalars(select(Task)
                                      .where(Task.chat_id == chat_id_db))

        if tasks:
            for task in tasks:
                await session.delete(task)

        await session.commit()

    except NoneChatException:
        raise
