from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

from functions import get_current_tasks
from models import FSMmodel

router: Router = Router()


@router.message(Command(commands=["mark_done"]),
                StateFilter(default_state))
async def process_mark_task_command(message: Message,
                                    state: FSMContext):
    id = message.from_user.id
    tasks = await get_current_tasks(id)
    if not tasks:
        await message.answer('На данный момент список актуальных задач пуст.')
    else:

    # await state.set_state(FSMmodel.add)
