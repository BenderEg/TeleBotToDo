import asyncio

from aiogram import Bot, Dispatcher

from functions import set_main_menu, set_schema
from models import BOT_TOKEN, storage, DbConnect
from routers import start, get_current, get_outdated, \
    mark_done, add_object, unspecific, calendar


async def main() -> None:

    bot: Bot = Bot(BOT_TOKEN)
    dp: Dispatcher = Dispatcher(storage=storage)

    dp.include_router(start.router)
    dp.include_router(get_current.router)
    dp.include_router(get_outdated.router)
    dp.include_router(mark_done.router)
    dp.include_router(calendar.router)
    dp.include_router(add_object.router)
    dp.include_router(unspecific.router)

    #with DbConnect() as db:
     #   set_schema(db.cur)

    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
