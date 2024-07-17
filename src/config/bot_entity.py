"""Файл со всеми сущностями, необходимыми для формирования фундамента бота"""

import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config.config import Config
from src.admin.tgClient import TelegramClient


class MyBot(Bot):
    '''Класс-обёртка над ботом aiogram для присвоения ему новых полей'''
    def __init__(self, tg_client: TelegramClient, token: str, **kwargs):
        super().__init__(token, **kwargs)
        self.tg_client = tg_client


tg_client = TelegramClient(Config.bot_token, base_url='https://api.telegram.org', admin_id=Config.admin_id)
bot = MyBot(tg_client=tg_client, token=Config.bot_token, default=DefaultBotProperties(parse_mode='HTML'))

dp = Dispatcher()

scheduler = AsyncIOScheduler()
scheduler.configure(timezone="Europe/Moscow")

logger = logging.getLogger(__name__)
logging.basicConfig(filename='reminder_bot.log', filemode='w', level=logging.INFO)
