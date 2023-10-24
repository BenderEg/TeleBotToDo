from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from pydantic import ValidationError

from models import FSMmodel, GeoFilter, TextFilter, Coords, redis
from settings import settings
from weather_models import RequestError,\
    create_modes_builder, get_locations_by_name, validate_locations,\
    create_locations_builder, SearchError


router: Router = Router()


@router.message(Command(commands=["location"]),
                StateFilter(default_state, FSMmodel.weather))
async def process_weather_command(message: Message, state: FSMContext):

    await state.set_state(FSMmodel.location)
    await message.answer('Отправьте геолокацию или наименование \
ближайшего населенного пункта.')


@router.message(StateFilter(FSMmodel.location),
                GeoFilter())
async def process_geo_object(message: Message,
                             state: FSMContext,
                             coords: Coords):
    try:
        await redis.set(f'coords:{message.chat.id}',
                        coords.model_dump_json(),
                        ex=settings.cache_exp)
        await state.set_state(FSMmodel.weather)
        await message.answer('Координаты успешно изменены. \
Для отображение погоды нажмите /weather.')
    except RequestError as p:
        await message.answer(str(p))
    except ValidationError as p:
        await message.answer(str(p))


@router.message(StateFilter(FSMmodel.location), TextFilter())
async def process_location_name(message: Message,
                                state: FSMContext,
                                text: str):
    try:
        response = await get_locations_by_name(text)
        data: list = await validate_locations(response=response)
        builder = await create_locations_builder(data)
        await message.answer(text='Выберите локацию из списка.\n\
Для выхода из режима нажмите /cancel:',
                             reply_markup=builder.as_markup())
    except RequestError as p:
        await message.answer(str(p))
    except SearchError as p:
        await message.answer(str(p))
    except ValidationError as p:
        await message.answer(str(p))


@router.callback_query(StateFilter(FSMmodel.location))
async def process_buttons_press(callback: CallbackQuery,
                                state: FSMContext):
    lat, lon = callback.data.split()
    coords = Coords(latitude=lat, longitude=lon)
    await redis.set(f'coords:{callback.from_user.id}',
                    coords.model_dump_json(),
                    ex=settings.cache_exp)
    builder = await create_modes_builder()
    await callback.message.edit_text(
        text='Выберите режим отображения погоды из списка.\n\
Для выхода из режима нажмите /cancel.\n\
Для выбора местоположения нажмите /location:',
        reply_markup=builder.as_markup())
    await state.set_state(FSMmodel.weather)
