from datetime import datetime
from uuid import UUID

from aiogram.fsm.storage.redis import RedisStorage, Redis, DefaultKeyBuilder
from aiogram.filters import BaseFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.types import Message
from pydantic import BaseModel

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


class TaskSchema(BaseModel):

    id: UUID
    task: str
    target_date: datetime
    task_status: str
