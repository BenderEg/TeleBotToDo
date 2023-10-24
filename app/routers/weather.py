from datetime import datetime
from json import loads

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, setup_dialogs, StartMode
from pydantic import ValidationError

from models import FSMmodel, GeoFilter, TextFilter, Coords, redis
from my_calendar import weather_dialog
from settings import settings
from weather_models import get_current_weather, convert_response_to_model,\
    CurrentData, send_current_weather, RequestError,\
    create_modes_builder, Modes, get_locations_by_name, validate_locations,\
    create_locations_builder, SearchError, get_forecast, validate_forecast,\
    prepare_forecast_output


router: Router = Router()
router.include_router(weather_dialog)
setup_dialogs(router)

@router.message(Command(commands=["weather"]),
                StateFilter(default_state, FSMmodel.weather))
async def process_weather_command(message: Message, state: FSMContext):

    coords_dict = await redis.get(f'coords:{message.from_user.id}')
    if coords_dict:
        builder = await create_modes_builder()
        await message.answer(text='Выберите режим отображения погоды из списка.\n\
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
                                dialog_manager: DialogManager,
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
            date = await redis.get(f'date:{callback.from_user.id}')
            if not date:
                await dialog_manager.start(FSMmodel.calendar,
                                           mode=StartMode.RESET_STACK)
            else:
                date = datetime.strptime(date, '%Y_%m_%d')
                time_diffrence = (date.date()-datetime.now().date()).days
                if time_diffrence == 0:
                    await callback.message.edit_text(
                        text='Для просмотра погоды на сегодня выберите \
соответствующий режим')
                else:
                    try:
                        response = await get_forecast(
                            latitude=coords.latitude,
                            longitude=coords.longitude)
                        forecast = await validate_forecast(response)
                        res = await prepare_forecast_output(forecast)
                        await callback.message.edit_text(
                            text=res, parse_mode='html')
                    except RequestError as p:
                        await callback.message.edit_text(p)
                    except ValidationError as p:
                        await callback.message.edit_text(p)
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
