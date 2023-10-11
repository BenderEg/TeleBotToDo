from aiogram import Router
from aiogram.types import Message

from models import TextFilter
from LEXICON import RU

router: Router = Router()


@router.message(TextFilter())
async def process_text_no_state(message: Message):
    await message.answer(text=RU.get('default_state'))
