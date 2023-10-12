from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, setup_dialogs, StartMode

from my_calendar import calendar_dialog

from models import FSMmodel


router: Router = Router()
router.include_router(calendar_dialog)
setup_dialogs(router)


@router.message(Command(commands=["calendar"]))
async def process_calendar_command(message: Message,
                                   dialog_manager: DialogManager,
                                   state: FSMContext):
    await dialog_manager.start(FSMmodel.calendar, mode=StartMode.RESET_STACK)
