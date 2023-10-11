from datetime import date

from aiogram.types import CallbackQuery
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog import Dialog, DialogManager, setup_dialogs, Window
from aiogram_dialog.widgets.text import Const

from models import FSMmodel, redis


async def on_date_selected(callback: CallbackQuery, widget,
                           manager: DialogManager,
                           selected_date: date):
    await manager.done()
    await redis.set(
        f'date:{callback.message.chat.id}',
        selected_date.strftime('%Y/%m/%d'), ex=30)
    await callback.message.edit_text(text=f'Вы в режиме ввода задачи.\n\
Выбранная дата: {selected_date}, введите задачу. Для выхода из режима нажмите /cancel.')


calendar_window = Window(
    Const("Выберите дату для записи"),
    Calendar(id='calendar', on_click=on_date_selected),
    state=FSMmodel.calendar,
)

dialog = Dialog(calendar_window)
