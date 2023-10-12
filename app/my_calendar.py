from datetime import date

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const

from models import FSMmodel, redis


async def calendar_in_add_mode(callback: CallbackQuery, widget,
                               manager: DialogManager,
                               selected_date: date):
    await manager.done()
    await redis.set(
        f'date:{callback.message.chat.id}',
        selected_date.strftime('%Y_%m_%d'), ex=300)
    await callback.message.edit_text(text=f'Вы в режиме ввода задачи.\n\
Выбранная дата: <b>{selected_date.strftime("%Y_%m_%d")}</b>, введите задачу. Для выхода из режима нажмите /cancel.',
                                     parse_mode='html')


async def calendar_mode(callback: CallbackQuery, widget,
                        manager: DialogManager,
                        selected_date: date):
    await manager.done()
    await redis.set(
        f'fsm:{callback.message.chat.id}:{callback.message.chat.id}:default:state',
        'FSMmodel:add')
    await redis.set(
        f'date:{callback.message.chat.id}',
        selected_date.strftime('%Y_%m_%d'), ex=300)
    await callback.message.edit_text(text=f'Выбранная дата: <b>{selected_date.strftime("%Y_%m_%d")}</b>. \
Введите задачу. Для выхода из режима нажмите /cancel.', parse_mode='html')

calendar_add_window = Window(
    Const("Выберите дату для записи."),
    Calendar(id='add_calendar', on_click=calendar_in_add_mode),
    state=FSMmodel.calendar,
)

calendar_window = Window(
    Const("Выберите дату."),
    Calendar(id='calendar', on_click=calendar_mode),
    state=FSMmodel.calendar,
)

add_dialog = Dialog(calendar_add_window)
calendar_dialog = Dialog(calendar_window)
