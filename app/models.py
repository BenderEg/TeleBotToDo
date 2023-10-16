from dataclasses import dataclass
from datetime import datetime
from time import sleep
from uuid import UUID


import psycopg2

from aiogram.fsm.storage.redis import RedisStorage, Redis, DefaultKeyBuilder
from aiogram.filters import BaseFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.types import Message
from psycopg2.extras import RealDictCursor

from settings import settings

BOT_TOKEN = settings.token
redis: Redis = Redis(host=settings.redis_host,
                     db=settings.redis_db,
                     encoding="utf-8",
                     decode_responses=True)
storage: RedisStorage = RedisStorage(redis=redis,
                                     key_builder=DefaultKeyBuilder(
                                         with_destiny=True))


class FSMmodel(StatesGroup):
    get_current = State()
    get_outdated = State()
    add = State()
    calendar = State()
    mark_done = State()


class Con:

    def __init__(self) -> None:

        self.con = psycopg2.connect(database=settings.postgres_db,
                                    user=settings.postgres_user,
                                    password=settings.postgres_password,
                                    host=settings.host,
                                    port=settings.port_db,
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
        if message.text:
            return {'text': message.text}
        return False


# not implemented
class OwnerValidation(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.id == settings.owner_id:
            return True
        else:
            return False


@dataclass
class TaskSchema():

    id: UUID
    task: str
    target_date: datetime
    task_status: str
