from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message


from functions import prepare_list_of_task, get_tasks, \
    filter_current_task, message_paginator
from models import FSMmodel

router: Router = Router()


@router.message(Command(commands=["get_current"]),
                StateFilter(default_state, FSMmodel.add))
async def process_get_current_command(message: Message):
    id = message.from_user.id
    all_tasks = await get_tasks(id, 'ASC')
    tasks = await filter_current_task(all_tasks)
    if not tasks:
        await message.answer('На данный момент список актуальных задач пуст.')
    else:
        res = await prepare_list_of_task(tasks)
        await message_paginator(res, message)
