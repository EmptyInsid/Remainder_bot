"""Файл хендлеров роутера (реакция на сообщения пользователя)"""

from datetime import timedelta, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from apscheduler.jobstores.base import JobLookupError, ConflictingIdError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.database.models import Task
from src.config.bot_entity import bot

import src.bot.utils as utils
import src.database.requests as rq
import src.texts.botMessages as txt
import src.keyboard.keyboard as kb


async def reminder_set(task: Task, chat_id: int, scheduler: AsyncIOScheduler, session: AsyncSession) -> None:
    '''
    Установка напоминания для задачи - час до, в дедлайн, час после дедлайна

    :param session: сессия бд бота
    :param scheduler: планировщик бота
    :param task: словарь с описанием задачи
    :param chat_id: id чата, куда будет отправлено напоминание
    '''

    try:
        scheduler.add_job(send_reminder,
                          args=[chat_id, task, session],
                          trigger='interval',
                          start_date=task.deadline - timedelta(hours=1),
                          end_date=task.deadline + timedelta(hours=1),
                          hours=1,
                          id=str(task.id))
    except JobLookupError:
        return


async def daily_reminder_set(chat_id: int, scheduler: AsyncIOScheduler, session: AsyncSession) -> None:
    '''
    Установка ежедневных напоминаний о задачах чата утром в 9:00

    :param session: сессия бд бота
    :param scheduler: планировщик бота
    :param chat_id: id чата, куда будет отправлен списка задач
    '''
    try:
        scheduler.add_job(send_daily_plane,
                          trigger='cron',
                          hour='9',
                          minute='00',
                          args=[chat_id, session],
                          id='chat_'+str(chat_id))
    except (JobLookupError, ConflictingIdError):
        return


async def remove_job(task_id: str, scheduler: AsyncIOScheduler) -> None:
    '''
    Удаление задачи из планировщика после выполнения

    :param scheduler: планировщик бота
    :param task_id: id задачи для удаления
    '''

    try:
        scheduler.remove_job(str(task_id).strip())
    except JobLookupError:
        return


async def remove_daily_job(chat_id: str, scheduler: AsyncIOScheduler) -> None:
    '''
    Удаление ежедневной задачи из планировщика после выполнения

    :param scheduler: планировщик бота
    :param chat_id: id чата для удаления
    '''

    try:
        scheduler.remove_job('chat_' + str(chat_id).strip())
    except JobLookupError:
        return


async def change_job_time(chat_id: int, new_time: datetime, task: Task,
                          scheduler: AsyncIOScheduler, session: AsyncSession) -> None:
    '''
    Изменение времени напоминания о задаче

    :param session: сессия бд бота
    :param scheduler: планировщик бота
    :param task: изменяемая задача
    :param chat_id: id чата с задачей
    :param new_time: новое время дедлайна
    '''

    try:

        scheduler.reschedule_job(str(task.id),
                                 trigger='interval',
                                 start_date=new_time - timedelta(hours=1),
                                 end_date=new_time + timedelta(hours=1),
                                 hours=1)
    except JobLookupError:
        await reminder_set(task, chat_id, scheduler, session)


async def send_reminder(chat_id: int, task: Task, session: AsyncSession) -> None:
    '''
    Задача отправки напоминания

    :param session: сессия бд бота
    :param chat_id: id чата, в который будет отправлено напоминание
    :param task: словарь с информацией о задаче (описание, ответственный, дедлайн)
    '''

    is_chat_on = await rq.get_is_chat_on(chat_id, session)

    if is_chat_on:
        update_task = await rq.get_task_by_id(chat_id, task.id, session)

        if update_task:

            task_mess = utils.make_beautiful_remainder(task)
            text = 'Напоминание! ' + _timer(update_task.deadline)

            await bot.send_message(chat_id, text + '\n' + task_mess, reply_markup=kb.done_kb(update_task.id))


async def send_daily_plane(chat_id: int, session: AsyncSession) -> None:
    '''
    Задача отправки списка задач для чата ежедневно в 9:00

    :param chat_id: id чата для отправки
    :param session: сессия бд бота
    '''
    is_chat_on = await rq.get_is_chat_on(chat_id, session)
    if is_chat_on:
        tasks = await rq.get_all_tasks(chat_id, session)
        response = utils.make_beautiful_remainder_list(tasks)
        await bot.send_message(chat_id, f'{txt.daily_plane_message}\n\n{response}')


def _timer(deadline: str) -> str:
    '''
    Высчитывает, сколько времени до дедлайна или он просрочен

    :param deadline: дедлайн задачи
    :return: строка с обратным отсчётом или уведомление о просроченном задании
    '''

    time_difference = datetime.fromisoformat(str(deadline)) - datetime.now()

    total_seconds = int(time_difference.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours < 0:
        return 'дедлайн просрочен на час!'

    return 'до дедлайна: {:02}:{:02}:{:02}'.format(hours, minutes, seconds)
