"""Файл утилит для обработки текстов"""

import re
from typing import Sequence

from dateutil.parser import parse, ParserError

from src.database.models import Task
from src.exceptions.myExeptions import *


async def executor_parser(text: str) -> str | None:
    '''
    Поиск упоминания ответственного в тексте задачи

    :param text: текст задачи
    :return: телеграм ник ответственного
    '''

    try:
        pattern = r'(?<!\w)@\w+'
        return re.findall(pattern, text)[0]
    except IndexError:
        return None


def _datetime_pattern_complete(deadline_before: str) -> str | None:
    '''
    Проверка на соответствие даты шаблонам DD.MM.YYYY HH:MM, HH:MM DD.MM.YYYY

    :param deadline_before: дедлайн до обработки
    :return: дедлайн после сопоставления и обработки
    '''

    datetime_pattern_complete = [
        r'\b\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{2}\b',  # DD.MM.YYYY HH:MM
        r'\d{1,2}:\d{2}\b \b\d{2}\.\d{2}\.\d{4}',  # HH:MM DD.MM.YYYY
    ]
    combined_pattern_complete = '|'.join(datetime_pattern_complete)
    if re.findall(combined_pattern_complete, deadline_before):
        return re.findall(combined_pattern_complete, deadline_before)[0]

    return None


def _datetime_pattern_without_time(deadline_before: str) -> str | None:
    '''
    Проверка на соответствие даты шаблоном DD.MM.YYYY

    :param deadline_before: дедлайн до обработки
    :return: дедлайн после сопоставления и обработки
    '''

    datetime_pattern_without_time = r'\b\d{2}\.\d{2}\.\d{4}'  # DD.MM.YYYY
    if re.findall(datetime_pattern_without_time, deadline_before):
        potential_datetime = re.findall(datetime_pattern_without_time, deadline_before)[0]
        return f"{potential_datetime} 10:00"

    return None


def _datetime_pattern_hhmm_ddmm(deadline_before: str) -> str | None:
    '''
    Проверка на соответствие даты шаблоном HH:MM DD.MM

    :param deadline_before: дедлайн до обработки
    :return: дедлайн после сопоставления и обработки
    '''

    datetime_pattern_hhmm_ddmm = r'\d{1,2}:\d{2}\b \b\d{2}\.\d{2}'  # HH:MM DD.MM

    if re.findall(datetime_pattern_hhmm_ddmm, deadline_before):
        potential_datetime = re.findall(datetime_pattern_hhmm_ddmm, deadline_before)[0]
        current_year = datetime.now().year
        return f"{potential_datetime}.{current_year}"

    return None


def _datetime_pattern_ddmm_hhmm(deadline_before: str) -> str | None:
    '''
    Проверка на соответствие даты шаблоном DD.MM HH:MM

    :param deadline_before: дедлайн до обработки
    :return: дедлайн после сопоставления и обработки
    '''

    datetime_pattern_ddmm_hhmm = r'\b\d{2}\.\d{2} \d{1,2}:\d{2}\b'  # DD.MM HH:MM

    if re.findall(datetime_pattern_ddmm_hhmm, deadline_before):
        potential_datetime = re.findall(datetime_pattern_ddmm_hhmm, deadline_before)[0]
        current_year = datetime.now().year
        potential_datetime_list = potential_datetime.split()
        return f"{potential_datetime_list[0]}.{current_year} {potential_datetime_list[1]}"

    return None


def _datetime_pattern_ddmm(deadline_before: str) -> str | None:
    '''
    Проверка на соответствие даты шаблоном DD.MM

    :param deadline_before: дедлайн до обработки
    :return: дедлайн после сопоставления и обработки
    '''

    datetime_pattern_ddmm = r'\b\d{2}\.\d{2}(?:\b|(?:\s+[а-яА-Яa-zA-Z]+))?'  # DD.MM

    if re.findall(datetime_pattern_ddmm, deadline_before):
        potential_datetime: str = re.findall(datetime_pattern_ddmm, deadline_before)[0]

        current_year = datetime.now().year
        potential_datetime = f"{potential_datetime}.{current_year}"
        return f"{potential_datetime} 10:00"

    return None


def _datetime_pattern_hhmm(deadline_before: str) -> str | None:
    '''
    Проверка на соответствие даты шаблонам HH:MM

    :param deadline_before: дедлайн до обработки
    :return: дедлайн после сопоставления и обработки
    '''

    datetime_pattern_complete = r'\d{1,2}:\d{2}\b'
    if re.findall(datetime_pattern_complete, deadline_before):
        return re.findall(datetime_pattern_complete, deadline_before)[0]

    return None


def _find_datetime_pattern(deadline_before: str) -> str | None:
    '''
    Проверка на соответствие одному из допустимых шаблонов

    :param deadline_before: дедлайн до обработки
    :return: дедлайн после сопоставления и обработки
    '''

    datetime_pattern_func = [
        _datetime_pattern_complete,
        _datetime_pattern_without_time,
        _datetime_pattern_hhmm_ddmm,
        _datetime_pattern_ddmm_hhmm,
        _datetime_pattern_ddmm,
        _datetime_pattern_hhmm,
    ]

    for datetime_pattern in datetime_pattern_func:
        potential_datetime = datetime_pattern(deadline_before)
        if potential_datetime:
            return potential_datetime

    return None


async def check_deadline_syntax(deadline_before: str) -> datetime | None:
    '''
    Проверка допустимости синтаксиса дедлайна в задаче

    :param deadline_before: строка дедлайна, полученная из задачи после тега #дедлайн
    :return: дедлайн в формате datetime
    '''

    try:

        potential_datetime = _find_datetime_pattern(deadline_before)

        if potential_datetime is None:
            return None

        deadline = parse(potential_datetime, dayfirst=True, yearfirst=False, fuzzy=False)
        return deadline

    except (IndexError, ParserError):
        raise DeadlineException


async def check_is_deadline_missed(datatime: datetime) -> None:
    '''
    Проверяем дату и время на актуальность (больше или меньше текущей даты).

    :param datatime: Выделенная из задачи дата дедлайна
    '''

    if datatime < datetime.now():
        raise DeadlineException


async def check_is_deadline_correct(deadline_before: str) -> datetime:
    '''
    Проверка дедлайна на корректность

    :param deadline_before: строка дедлайна, полученная из задачи после тега #дедлайн
    :return: Выделенная из задачи дата дедлайна
    '''

    try:
        deadline = await check_deadline_syntax(deadline_before)
        if deadline:
            await check_is_deadline_missed(deadline)
        return deadline
    except DeadlineException:
        raise


async def parse_raw_deadline(text: str) -> str | None:
    '''
    Выделение времени дедлайна из строки после тега #дедлайн

    :param text: текст задачи
    :return: дедлайн строкой
    '''

    if text.find('#дедлайн') != -1:
        deadline = text.split('#дедлайн')[1].strip()
        if deadline == '':
            raise DeadlineException
        return deadline
    else:
        return None


async def deadline_parser(deadline_before: str) -> datetime | None:
    '''
    Получение даты из текста в формате datetime

    :param deadline_before: строка дедлайна, полученная из задачи после тега #дедлайн
    :return: дедлайн в формате datetime, если он есть в задаче
    '''

    try:
        if deadline_before:
            deadline = await check_is_deadline_correct(deadline_before)
            return deadline
        return None

    except (IndexError, DeadlineException):
        raise DeadlineException


async def description_parse(text: str, executor: str, deadline_before: str) -> str:
    '''
    Выделение описания задачи

    :param deadline_before: строка дедлайна, полученная из задачи после тега #дедлайн
    :param executor: ответственный в тексте задачи
    :param text: изначальный текст задачи
    :return: строка с описанием задачи (без ответственного и дедлайна)
    '''

    try:
        description = text.split('#задача')[1].strip()
        if deadline_before:
            description = description.replace(deadline_before, '', 1)
            description = description.replace('#дедлайн', '', 1)

        if executor:
            description = description.replace(executor, '', 1)

        if description.strip() == '':
            raise DescriptionException
        else:
            return description

    except Exception:
        raise DescriptionException


async def task_parser(text: str) -> dict:
    '''
    Разделение строки с задачей на составляющие: описание задачи, ответственный и дедлайн

    :param text: сырая строка с задачей
    :return: словарь с отделёнными составляющими задачи
    '''

    executor = await executor_parser(text)
    deadline_before = await parse_raw_deadline(text)

    try:
        parse_task = {
            'id': '',
            'executor': executor,
            'deadline': await deadline_parser(deadline_before),
            'description': await description_parse(text, executor, deadline_before),
        }
    except (DescriptionException, DeadlineException, ExecutorException):
        raise

    return parse_task


async def change_time_parse(text: str) -> dict:
    '''
    Парс id и времени для смены

    :param text: текст после команды /change_time
    :return: словарь с id задачи и новым временем
    '''
    try:

        split_mess = text.split(maxsplit=2)
        task_id = int(split_mess[1])
        task_new_time = await check_is_deadline_correct(split_mess[2])

        return {'task_id': task_id, 'task_new_time': task_new_time}
    except (IndexError, MyException):
        raise


def make_beautiful_remainder(task: Task) -> str:
    '''
    Формирование строки напоминания

    :param task: задача из базы данных
    :return: оформленная строка для пользователя
    '''

    deadline = task.deadline
    executor = task.executor

    if task.deadline is None:
        deadline = 'не назначен'

    if task.executor is None:
        executor = 'не назначен'

    return (f'📍ID: {task.id}\n'
            f'📝Описание: {task.description}\n'
            f'⏰Дедлайн: {deadline}\n'
            f'🧑🏼‍💻Ответственный: {executor}\n\n')


def make_beautiful_remainder_list(tasks: Sequence[Task]) -> str:
    '''
    Формирование списка напоминания

    :param tasks: задачи из базы данных
    :return: оформленный список для пользователя
    '''

    if tasks:
        response = '🗓Задачи для этого чата:🗓\n\n'
        overdue = '\n⛔️Просроченные задачи:⛔️\n\n'

        for task in tasks:
            text_mess = make_beautiful_remainder(task)
            if task.deadline is not None and task.deadline < datetime.now():
                overdue += text_mess
            else:
                response += text_mess

        if response == '🗓Задачи для этого чата:🗓\n\n':
            response += 'Актуальных задач нет!'
        if overdue == '\n⛔️Просроченные задачи:⛔️\n\n':
            overdue += 'Просроченных задач нет!'

        response += overdue

    else:
        response = 'Задач для этого чата нет.'

    return response
