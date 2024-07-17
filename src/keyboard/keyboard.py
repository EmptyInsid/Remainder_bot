"""Файл клавиатур"""

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def done_kb(task_id: int) -> InlineKeyboardMarkup:
    '''Кнопка, чтобы отметить задачу выполненной'''

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Выполнено✅', callback_data=f'done_{task_id}'))
    return keyboard.adjust(1).as_markup()
