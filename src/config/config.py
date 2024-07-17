"""Файл данных конфигурации"""

import os

from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass

load_dotenv(find_dotenv())


@dataclass
class Config:
    bot_token: str = os.getenv('TOKEN')
    db_url: str = os.getenv('DB_URL')
    admin_id: str = os.getenv('ADMIN_ID')
