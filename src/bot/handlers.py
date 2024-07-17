"""Файл хендлеров роутера (реакция на сообщения пользователя)"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.database.models import Task
from src.exceptions.myExeptions import *
from src.config.bot_entity import logger, bot

import src.bot.utils as utils
import src.bot.scheduler as sh
import src.database.requests as rq


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    '''Стартовое сообщение для запуска бота в личной переписке'''

    # добавляет чат в БД БЕЗ включения на отслеживание
    await rq.set_chat(message.chat.id, session)
    await message.answer(txt.start_message)


@router.message(Command('help'))
async def cmd_help(message: Message):
    '''Команда получения информационного сообщения с инструкцией по использованию бота'''

    await message.answer(txt.help_message)


@router.message(Command('bot_on'))
async def cmd_bot_on(message: Message, scheduler: AsyncIOScheduler, session: AsyncSession) -> None:
    '''Команда включения бота для обработки данного чата'''

    try:
        await rq.set_chat_on(message.chat.id, session)
        await sh.daily_reminder_set(message.chat.id, scheduler, session)

        await message.answer(txt.bot_on)

    except MyException as err:
        await message.answer(f'{err}')


@router.message(Command('bot_off'))
async def cmd_bot_off(message: Message, session: AsyncSession):
    '''Команда отключения бота от обработки данного чата'''

    try:
        await rq.set_chat_off(message.chat.id, session)
        await message.answer(txt.bot_off)

    except MyException as err:
        await message.answer(f'{err}')


@router.message(Command('change_time'))
async def cmd_change_time(message: Message, scheduler: AsyncIOScheduler, session: AsyncSession):
    '''Команда изменения дедлайна для ранее добавленной задачи'''

    try:

        task_info = await utils.change_time_parse(message.text)
        await rq.change_task_time(message.chat.id, task_info['task_id'], task_info['task_new_time'], session)

        task_db = await rq.get_task_by_id(message.chat.id, task_info['task_id'], session)
        await sh.change_job_time(message.chat.id, task_info['task_new_time'], task_db, scheduler, session)

        await message.answer(txt.change_message)

    except MyException as err:
        await message.answer(f'{err}')

    except (IndexError, ValueError) as err:
        await message.answer(txt.change_time_err)
        logger.info(err)

    except Exception as err:
        await message.answer(txt.baseException)
        bot.tg_client.send_message_to_admin(f'Bot:{await bot.get_my_name()}\n'
                                            f'Error: {err.__class__}\n'
                                            f'{err}\n'
                                            f'Chat: {message.chat.id}')


@router.message(Command('get_tasks'))
async def cmd_get_tasks(message: Message, session: AsyncSession):
    '''Получение всех задач для данного чата'''

    try:
        tasks = await rq.get_all_tasks(message.chat.id, session)
        response = utils.make_beautiful_remainder_list(tasks)
        await message.answer(response)

    except MyException as err:
        await message.answer(f'{err}')

    except Exception as err:
        await message.answer(txt.baseException)
        bot.tg_client.send_message_to_admin(f'Bot:{await bot.get_my_name()}\n'
                                            f'Error: {err.__class__}\n'
                                            f'{err}\n'
                                            f'Chat: {message.chat.id}')


@router.message(Command('done'))
async def cmd_done(message: Message, scheduler: AsyncIOScheduler, session: AsyncSession):
    '''Отметить задачу выполненной и удалить из БД'''

    try:

        task_id = message.text.split()[1]

        await rq.delete_task(message.chat.id, int(task_id), session)
        await sh.remove_job(task_id, scheduler)

        await message.answer(txt.done_message + task_id)

    except (IndexError, ValueError):
        await message.answer(txt.done_err)

    except MyException as err:
        await message.answer(f'{err}')

    except Exception as err:
        await message.answer(txt.baseException)
        bot.tg_client.send_message_to_admin(f'Bot:{await bot.get_my_name()}\n'
                                            f'Error: {err.__class__}\n'
                                            f'{err}\n'
                                            f'Chat: {message.chat.id}')


@router.message(Command('done_all'))
async def cmd_done_all(message: Message, scheduler: AsyncIOScheduler, session: AsyncSession):
    '''Отметить все задачи чата выполненными и удалить из БД'''

    try:

        all_tasks = await rq.get_all_tasks(message.chat.id, session)
        for task in all_tasks:
            await rq.delete_task(message.chat.id, int(task.id), session)
            await sh.remove_job(task.id, scheduler)

        await message.answer(txt.done_all_message)

    except MyException as err:
        await message.answer(f'{err}')

    except Exception as err:
        await message.answer(txt.baseException)
        bot.tg_client.send_message_to_admin(f'Bot:{await bot.get_my_name()}\n'
                                            f'Error: {err.__class__}\n'
                                            f'{err}\n'
                                            f'Chat: {message.chat.id}')


@router.message(F.text.contains('#задача'))
async def get_task(message: Message, scheduler: AsyncIOScheduler, session: AsyncSession):
    '''Обработка сообщения с тегом #задача - добавление в БД и назначение расписания'''

    try:
        task = await utils.task_parser(message.text)
        db: Task = await rq.set_task(message.chat.id, task, session)

        if db.deadline is not None:
            await sh.reminder_set(db, message.chat.id, scheduler, session)

        await message.answer(f'Новая задача успешно добавлена!\nID новой задачи: {db.id}')

    except MyException as err:
        await message.answer(f'{err}')
        logger.info(err)

    except Exception as err:
        bot.tg_client.send_message_to_admin(f'Bot:{await bot.get_my_name()}\n'
                                            f'Error: {err.__class__}\n'
                                            f'{err}\n'
                                            f'Chat: {message.chat.id}')


@router.callback_query(F.data.startswith('done_'))
async def done_keyboard(callback: CallbackQuery, scheduler: AsyncIOScheduler, session: AsyncSession):
    '''Отметить выполненной задачу через кнопку'''

    try:
        await callback.answer()

        task_id = callback.data.split('_')[1]

        await rq.delete_task(callback.message.chat.id, int(task_id), session)
        await sh.remove_job(task_id, scheduler)

        await callback.message.answer(txt.done_message + task_id)

    except MyException as err:
        await callback.message.answer(f'{err}')

    except Exception as err:
        await callback.message.answer(txt.baseException)
        bot.tg_client.send_message_to_admin(f'Bot:{await bot.get_my_name()}\n'
                                            f'Error: {err.__class__}\n'
                                            f'{err}\n'
                                            f'Chat: {callback.message.chat.id}')

