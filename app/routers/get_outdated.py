from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message

from functions import prepare_list_of_task, get_tasks, filter_outdated_task
from models import FSMmodel


router: Router = Router()


@router.message(Command(commands=["get_outdated"]),
                StateFilter(default_state, FSMmodel.add))
async def process_get_outdated_command(message: Message):
    id = message.from_user.id
    all_tasks = await get_tasks(id, 'DESC')
    tasks = await filter_outdated_task(all_tasks)
    if not tasks:
        await message.answer(
            'Cписок просроченных задач за прошедшую неделю пуст.')
    else:
        res = await prepare_list_of_task(tasks)
        await message.answer(text=res, parse_mode='html')
