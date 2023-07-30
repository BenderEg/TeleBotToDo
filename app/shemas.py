from typing import List
from aiogram.types import Message
from aiogram.filters import BaseFilter
from db_code import db_close, db_open
from dotenv import load_dotenv
from os import environ

load_dotenv()


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
            return {'response': response}
        else:
            return False


class OwnerValidation(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.id == int(environ['OWNER_ID']):
            return True
        else:
            return False


help_response = '''Я могу хранить твои задачи:)\n
Доступные команды:\n
/start - позвляет получить перечень команд и авторизоваться в системе;\n
/help - выводит эту подсказку;\n
/get - позволяет получить перечень актуальных задач;\n
/add - позволяет добавить задачу в перечень (после ввода этой команды последующие текстовые\n сообщения рассматриваются как задачи);\n
/del - позволяет удалить задачу из перечня (после ввода этой команды бот переходит в режим удаления,\nудаление регистронезависимое, также возможно по части наименования);\n
/cancel - позвояет выйти из режима добавления или удаления задач.
'''