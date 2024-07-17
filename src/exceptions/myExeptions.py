"""Файл с классами пользовательских ошибок"""

from datetime import datetime

import src.texts.botMessages as txt


class MyException(Exception):
    '''Базовый класс пользовательских ошибок'''
    def __init__(self, message: str = txt.baseException, extra_info: str = str(datetime.now())):
        super().__init__(message)


class ExecutorException(MyException):
    '''Ошибка при выделении ответственного в задаче'''
    def __init__(self, message: str = txt.executorException, extra_info: str = str(datetime.now())):
        super().__init__(message, extra_info)


class DeadlineException(MyException):
    '''Ошибка при выделении дедлайн'''
    def __init__(self, message: str = txt.deadlineException, extra_info: str = str(datetime.now())):
        super().__init__(message, extra_info)


class DescriptionException(MyException):
    '''Ошибка при выделении описания задачи'''
    def __init__(self, message: str = txt.descriptionException, extra_info: str = str(datetime.now())):
        super().__init__(message, extra_info)


class NoneChatException(MyException):
    '''Ошибка при поиске чата в базе данных'''
    def __init__(self, message: str = txt.noneChatException, extra_info: str = str(datetime.now())):
        super().__init__(message, extra_info)


class NoneTaskException(MyException):
    '''Ошибка при поиске задачи в базе данных'''
    def __init__(self, message: str = txt.noneTaskException, extra_info: str = str(datetime.now())):
        super().__init__(message, extra_info)
