from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

from functions import start
from models import FSMmodel, DbConnect, TextFilter
from LEXICON import RU

router: Router = Router()


@router.message(Command(commands=["start"]), StateFilter(default_state))
async def process_start_command(message: Message):
    id, name = message.from_user.id, message.from_user.first_name
    await start(id, name)
    await message.answer(f'Привет, {name}!\n{RU.get("start")}')


@router.message(Command(commands=["help"]), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(f'{RU.get("help")}')
