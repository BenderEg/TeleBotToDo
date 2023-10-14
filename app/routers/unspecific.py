from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from models import TextFilter
from LEXICON import RU

router: Router = Router()


@router.message(Command(commands='cancel'))
async def process_canel_command(message: Message,
                                state: FSMContext):
    await message.answer('Выберите команду из перечня.')


@router.message(TextFilter())
async def process_text_no_state(message: Message):
    await message.answer(text=RU.get('default_state'))
