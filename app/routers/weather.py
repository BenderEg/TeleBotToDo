from json import loads

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from pydantic import ValidationError

from models import FSMmodel, GeoFilter, TextFilter, Coords, redis
from settings import settings
from weather_models import get_current_weather, convert_response_to_model, \
    CurrentData, prepare_current_output, send_current_weather, RequestError,\
    create_modes_builder, Modes


router: Router = Router()


@router.message(Command(commands=["weather"]),
                StateFilter(default_state, FSMmodel.add))
async def process_weather_command(message: Message, state: FSMContext):

    builder = await create_modes_builder()
    await message.answer(text='Выберите режим отображения погоды из списка.\n\
Для выхода из режима нажмите /cancel:',
                         reply_markup=builder.as_markup())
    await state.set_state(FSMmodel.weather)


@router.callback_query(StateFilter(FSMmodel.weather))
async def process_buttons_press(callback: CallbackQuery,
                                state: FSMContext):

    if int(callback.data) == Modes.CURRENT_SHORT.value:
        coords_dict = await redis.get(f'coords:{callback.from_user.id}')
        if coords_dict:
            coords = Coords(**loads(coords_dict))
            try:
                res = await send_current_weather(latitude=coords.latitude,
                                                 longitude=coords.longitude,
                                                 class_name=CurrentData)
                await callback.message.edit_text(res)
            except RequestError as p:
                await callback.message.edit_text(p)
            except ValidationError as p:
                await callback.message.edit_text(p)
        else:
            await callback.message.edit_text(
                'Отправьте геолокацию или наименование \
ближайшего населенного пункта.')


@router.message(StateFilter(FSMmodel.weather),
                Command(commands='cancel'))
async def process_cancel_command(message: Message,
                                 state: FSMContext):
    await message.answer('Вы вышли из режима погоды.\n\
Для создания задачи нажмите /add_object.\n\
Для отметки выполненных задач нажмите /mark_done.\n\
Для просмотра актуальных задач нажмите /get_current.')
    await state.set_state(state=None)


@router.message(StateFilter(FSMmodel.weather), GeoFilter())
async def process_geo_object(message: Message,
                             state: FSMContext,
                             coords: Coords):
    try:
        res = await send_current_weather(latitude=coords.latitude,
                                         longitude=coords.longitude,
                                         class_name=CurrentData)
        await message.answer(res)
        await redis.set(f'coords:{message.chat.id}',
                        coords.model_dump_json(),
                        ex=settings.cache_exp)
    except RequestError as p:
        await message.answer(p)
    except ValidationError as p:
        await message.answer(p)

    await state.set_state(state=None)

'''
@router.message(StateFilter(FSMmodel.weather), TextFilter())
async def process_location_name(message: Message, state: FSMContext):
    longitude = message.location.longitude
    latitude = message.location.latitude
    response = await get_current_weather(latitude=latitude,
                                 longitude=longitude)
    data: Data = await convert_response_to_model(
        response=response, _class=Data)
    res = await prepare_output(data)
    await message.answer(res)
    await state.set_state(state=None)
'''