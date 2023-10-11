from aiogram.filters import Command
from aiogram.types import Message


from functions import set_schema
from shemas import get_response, UserValidation, \
    TextFilter, OwnerValidation, help_response
from dotenv import load_dotenv
import requests


import asyncio
from aiogram import Bot, Dispatcher

#from congif import set_main_menu
from routers import start, get_current, get_outdated, \
    mark_done, add_object, unspecific
from models import BOT_TOKEN, storage, DbConnect


async def main() -> None:

    # Инициализируем бот и диспетчер
    bot: Bot = Bot(BOT_TOKEN)
    dp: Dispatcher = Dispatcher(storage=storage)

    # Регистриуем роутеры в диспетчере

    dp.include_router(start.router)
    dp.include_router(get_current.router)
    dp.include_router(get_outdated.router)
    dp.include_router(mark_done.router)
    dp.include_router(add_object.router)
    dp.include_router(unspecific.router)

    #with DbConnect() as db:
     #   set_schema(db.cur)

    # создаем меню
    # await set_main_menu(bot)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
