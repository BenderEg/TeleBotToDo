from datetime import datetime
from uuid import UUID

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis, DefaultKeyBuilder
from aiogram.filters import BaseFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.types import Message
from pydantic import BaseModel, ConfigDict

from settings import settings

BOT_TOKEN = settings.token
redis: Redis = Redis(host=settings.redis_host,
                     db=settings.redis_db,
                     encoding="utf-8",
                     decode_responses=True)
storage: RedisStorage = RedisStorage(redis=redis,
                                     key_builder=DefaultKeyBuilder(
                                         with_destiny=True))
bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher(storage=storage)


class FSMmodel(StatesGroup):
    get_current = State()
    get_outdated = State()
    add = State()
    calendar = State()
    mark_done = State()
    weather = State()
    location = State()
    data_for_weather = State()


class TextFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.text:
            return {'text': message.text}
        return False


class Coords(BaseModel):

    latitude: float
    longitude: float


class GeoFilter(BaseFilter):
    async def __call__(self, message: Message) -> Coords | bool:
        if message.location:
            coords = Coords(latitude=message.location.latitude,
                            longitude=message.location.longitude)
            return {'coords': coords}
        return False


# not implemented
class OwnerValidation(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.id == settings.owner_id:
            return True
        else:
            return False


class TaskSchema(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task: str
    target_date: datetime
    task_status: str
