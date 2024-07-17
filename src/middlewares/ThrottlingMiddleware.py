from cachetools import TTLCache
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

# Максимальный размер кэша - 10000 ключей, а время жизни ключа - 1 секунд
CACHE = TTLCache(maxsize=10_000, ttl=1)


class ThrottlingMiddleware(BaseMiddleware):
    '''Middleware для предотвращения тротлинга'''

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user: User = data.get('event_from_user')

        if user.id in CACHE:
            return

        CACHE[user.id] = True

        return await handler(event, data)
