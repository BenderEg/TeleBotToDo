from dataclasses import dataclass
from datetime import datetime
from os import environ
from time import sleep
from uuid import UUID


import psycopg2

from aiogram.fsm.storage.redis import RedisStorage, Redis, DefaultKeyBuilder
from aiogram.filters import BaseFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


load_dotenv('.envdev')

BOT_TOKEN = environ["TOKEN"]
redis: Redis = Redis(host=environ["REDIS_HOST"],
                     db=environ['REDIS_DB'],
                     encoding="utf-8",
                     decode_responses=True)
storage: RedisStorage = RedisStorage(redis=redis,
                                     key_builder=DefaultKeyBuilder(
                                         with_destiny=True))


commands = {'/add, /calendar', '/get_outdated',
            '/get_current', '/help', '/start'}


class FSMmodel(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    get_current = State()  # Состояние тренировки
    get_outdated = State()
    add = State()  # Состояние добавления объектов
    calendar = State()
    mark_done = State()


class Con:

    def __init__(self) -> None:

        self.con = psycopg2.connect(database=environ["POSTGRES_DB"],
                                    user=environ["POSTGRES_USER"],
                                    password=environ["POSTGRES_PASSWORD"],
                                    host=environ["HOST"],
                                    port=environ["PORT_DB"],
                                    cursor_factory=RealDictCursor)
        self.cur = self.con.cursor()


class DbConnect:

    def __init__(self) -> None:
        while True:
            try:
                self.db = Con()
                print('successuly connected')
                break
            except Exception as p:
                print('fail to connect to database')
                print(f'Error: {p}')
                sleep(1)

    def __enter__(self):
        return self.db

    def __exit__(self, *args):
        self.db.con.commit()
        self.db.con.close()
        return False


class TextFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.text and message.text not in commands:
            return {'text': message.text}
        return False


# not implemented
class OwnerValidation(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.id == int(environ['OWNER_ID']):
            return True
        else:
            return False


@dataclass
class Task():

    id: UUID
    task: str
    target_date: datetime
    task_status: str
