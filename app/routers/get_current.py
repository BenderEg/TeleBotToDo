from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message


from functions import prepare_list_of_task, get_tasks
from models import FSMmodel

router: Router = Router()


@router.message(Command(commands=["get_current"]),
                StateFilter(default_state, FSMmodel.add))
async def process_get_current_command(message: Message):
    id = message.from_user.id
    tasks = await get_tasks(id, 'current', 'ASC')
    if not tasks:
        await message.answer('На данный момент список актуальных задач пуст.')
    else:
        res = await prepare_list_of_task(tasks)
        await message.answer(text=res, parse_mode='html')
