from json import loads

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from pydantic import ValidationError

from models import FSMmodel, Coords, redis
from weather_models import CurrentData, send_current_weather, RequestError,\
    create_modes_builder, Modes, send_forecast


router: Router = Router()


@router.message(Command(commands=["weather"]),
                StateFilter(default_state, FSMmodel.weather))
async def process_weather_command(message: Message, state: FSMContext):

    coords_dict = await redis.get(f'coords:{message.from_user.id}')
    if coords_dict:
        builder = await create_modes_builder()
        await message.answer(
            text='Выберите режим отображения погоды из списка.\n\
Для выхода из режима нажмите /cancel.\n\
Для выбора местоположения нажмите /location:',
            reply_markup=builder.as_markup())
        await state.set_state(FSMmodel.weather)
    else:
        await state.set_state(FSMmodel.location)
        await message.answer('Отправьте геолокацию или наименование \
ближайшего населенного пункта.')


@router.callback_query(StateFilter(FSMmodel.weather))
async def process_buttons_press(callback: CallbackQuery,
                                state: FSMContext):
    status = int(callback.data)
    coords_dict = await redis.get(f'coords:{callback.from_user.id}')
    if coords_dict:
        coords = Coords(**loads(coords_dict))
        if status == Modes.CURRENT_SHORT.value \
                or status == Modes.CURRENT_LONG.value:
            try:
                res = await send_current_weather(latitude=coords.latitude,
                                                 longitude=coords.longitude,
                                                 class_name=CurrentData,
                                                 mode=status)
                await callback.message.edit_text(res)
            except RequestError as p:
                await callback.message.edit_text(p)
            except ValidationError as p:
                await callback.message.edit_text(p)
        elif status == Modes.FORECAST.value:
            try:
                res = await send_forecast(
                            latitude=coords.latitude,
                            longitude=coords.longitude)
                await callback.message.edit_text(
                            text=res, parse_mode='html')
            except RequestError as p:
                await callback.message.edit_text(p)
            except ValidationError as p:
                await callback.message.edit_text(p)
        await state.set_state(state=None)
    else:
        await state.set_state(FSMmodel.location)
        await callback.message.edit_text(
                'Отправьте геолокацию или наименование \
ближайшего населенного пункта.')


@router.message(StateFilter(FSMmodel.weather, FSMmodel.location),
                Command(commands='cancel'))
async def process_cancel_command(message: Message,
                                 state: FSMContext):
    await message.answer('Вы вышли из режима погоды.\n\
Для создания задачи нажмите /add_object.\n\
Для отметки выполненных задач нажмите /mark_done.\n\
Для просмотра актуальных задач нажмите /get_current.')
    await state.set_state(state=None)
