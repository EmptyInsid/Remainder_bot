"""Файл запуска"""

import asyncio
import logging

from src.bot.handlers import router
from src.config.bot_entity import bot, dp, MyBot, scheduler
from src.database.engine import create_db, drop_db, async_session
from src.middlewares.SchedulerMiddlewares import SchedulerMiddleware
from src.middlewares.ShadowBanMiddleware import ShadowBanMiddleware
from src.middlewares.ThrottlingMiddleware import ThrottlingMiddleware
from src.middlewares.DBSessionMiddleware import DBSessionMiddleware


async def on_startup(bot: MyBot):
    '''Функция срабатывает при включении бота'''

    run_param = False
    if run_param:
        await drop_db()

    await create_db()
    bot.tg_client.send_message_to_admin(f'Bot: {await bot.get_my_name()} start working')


async def on_shutdown(bot: MyBot):
    '''Функция срабатывает при выключении бота'''

    bot.tg_client.send_message_to_admin(f'Bot: {await bot.get_my_name()} stopped working')


def middleware_register():
    '''Функция регистрации всех middleware'''

    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.middleware.register(DBSessionMiddleware(async_session))
    dp.update.middleware.register(ShadowBanMiddleware())
    dp.update.middleware(ThrottlingMiddleware())


async def main():

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(router)
    middleware_register()

    try:
        scheduler.start()

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info('Bot stopped working')
