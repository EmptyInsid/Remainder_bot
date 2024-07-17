from typing import Any, Awaitable, Callable, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Chat

import src.database.requests as rq


class ShadowBanMiddleware(BaseMiddleware):
    '''Middleware для регулировки состояний включения и выключения бота'''
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        if event.dict()['message']:
            command: str = event.dict()['message']['text']

            if command:
                if command.startswith('/bot') or command.startswith('/start') or command.startswith('/help'):
                    return await handler(event, data)

                chat: Chat = data.get('event_chat')
                session: AsyncSession = data.get('session')
                chat_on = await rq.get_is_chat_on(chat.id, session)

                if not chat_on:
                    return

        return await handler(event, data)
