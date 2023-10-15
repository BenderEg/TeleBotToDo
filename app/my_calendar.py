from datetime import date, datetime

from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const

from models import FSMmodel, redis
from settings import settings

async def calendar_mode(callback: CallbackQuery, widget,
                        manager: DialogManager,
                        selected_date: date):
    await manager.done()
    if selected_date < datetime.now().date():
        await callback.message.edit_text(
            text=f'Выбранная дата <b>{selected_date.strftime("%Y_%m_%d")}</b> \
 менее текущей даты. Нажмите /add или /calendar для повторного выбора даты.',
            parse_mode='html')
    else:
        await redis.set(
            f'fsm:{callback.message.chat.id}:{callback.message.chat.id}:default:state',
            'FSMmodel:add')
        await redis.set(
            f'date:{callback.message.chat.id}',
            selected_date.strftime('%Y_%m_%d'), ex=settings.cache_exp)
        await callback.message.edit_text(
            text=f'Выбранная дата: <b>{selected_date.strftime("%Y_%m_%d")}</b>. \
Введите задачу. Для выхода из режима ввода задачи нажмите /cancel.\n\
Для смены даты нажмите /calendar.', parse_mode='html')


calendar_window = Window(
    Const("Выберите дату."),
    Calendar(id='calendar', on_click=calendar_mode),
    state=FSMmodel.calendar,
)

calendar_dialog = Dialog(calendar_window)
add_dialog = Dialog(calendar_window)
