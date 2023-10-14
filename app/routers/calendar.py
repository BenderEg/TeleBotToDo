from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from aiogram.fsm.state import default_state


from my_calendar import calendar_dialog

from models import FSMmodel
from routers.add_object import setup_dialogs

router: Router = Router()
router.include_router(calendar_dialog)
setup_dialogs(router)


@router.message(Command(commands=["calendar"]),
                StateFilter(default_state, FSMmodel.add))
async def process_calendar_command(message: Message,
                                   dialog_manager: DialogManager,
                                   state: FSMContext):
    await dialog_manager.start(FSMmodel.calendar, mode=StartMode.RESET_STACK)
