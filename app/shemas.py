from typing import List
from aiogram.types import Message
from aiogram.filters import BaseFilter
from db_code import db_close, db_open


def get_response(tasks: List[tuple]) -> str:
    res = ''
    for i, ele in enumerate(tasks, 1):
        res += f'{i}. {ele[0]}\n'
    return res


class TextFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.text:
            return {'text': message.text}
        return False


class UserValidation(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        con, cursor = db_open()
        cursor.execute('SELECT id, status FROM public.users WHERE id=%s', (
            message.from_user.id,
        ))
        response = cursor.fetchone()
        db_close(con)
        if response:
            print(response)
            return {'response': response}
        else:
            return False
