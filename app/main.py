from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from os import environ
from db_code import db_close, db_open
from shemas import Token, get_response, UserValidation, TextFilter
from dotenv import load_dotenv

load_dotenv()

tok = Token()
bot: Bot = Bot(token=environ["TOKEN"])
dp: Dispatcher = Dispatcher()  # обработчик запросов
# перечень доступных команд
commands_lst = ('/start', '/help', '/get', '/add', '/del', '/cancel')

# /start - выдает общую информацию
# /help - выводит меню
# /get - выводит списко задач
# /add - переход в режим регистрации задач
# /del - переход в режим удаления задач


@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    con, cursor = db_open()
    cursor.execute('SELECT id, status FROM public.users WHERE id=%s', (
        message.from_user.id,
    ))
    response = cursor.fetchone()
    if response:
        cursor.execute('UPDATE public.users SET status=%s WHERE id=%s', (
            'Idle', message.from_user.id,
        ))
    else:
        cursor.execute('INSERT INTO public.users(id, status) \
                       VALUES (%s, %s)', (
            message.from_user.id, 'Idle'
        ))
    db_close(con)
    res = '\n'.join(commands_lst)
    await message.answer(f'Привет, {message.from_user.first_name}!\
                         \nДоступные комады:\n{res}')


@dp.message(Command(commands=['help']), UserValidation())
async def process_help_command(message: Message):
    await message.answer('Я могу хранить твои задачи:)')


@dp.message(Command(commands=['cancel']), UserValidation())
async def process_cancel_command(message: Message):
    con, cursor = db_open()
    cursor.execute('UPDATE public.users SET status=%s WHERE id=%s', (
            'Idle', message.from_user.id,
        ))
    db_close(con)
    await message.answer('Теперь я в режиме ожидания')


@dp.message(Command(commands=['get']), UserValidation())
async def process_get_command(message: Message):
    con, cursor = db_open()
    cursor.execute('SELECT task FROM public.table WHERE user_id=%s', (
        message.from_user.id,)
    )
    tasks = cursor.fetchall()
    db_close(con)
    if len(tasks) != 0:
        res = get_response(tasks)
        await message.answer(f'Привожу перечень ваших задач: \n{res}')
    else:
        await message.answer(
            'Нет текущих задач, для добавления выберите команду /add.')


@dp.message(Command(commands=['add']), UserValidation())
async def process_add_command(message: Message):
    con, cursor = db_open()
    cursor.execute('UPDATE public.users SET status=%s WHERE id=%s', (
        'Add', message.from_user.id,
    ))
    db_close(con)
    await message.answer(
        'Введите задачу: каждая задача - новое сообщение:). \
Для завершения выберите команду /cancel.'
    )


@dp.message(Command(commands=['del']), UserValidation())
async def process_del_command(message: Message):
    con, cursor = db_open()
    cursor.execute('UPDATE public.users SET status=%s WHERE id=%s', (
        'Del', message.from_user.id,
    ))
    db_close(con)
    await message.answer(
        'Введите задачу для удаления: каждая задача - новое сообщение:). \
Для завершения выберите команду /cancel.'
        )


@dp.message(UserValidation(), TextFilter())
async def process_text_messages_is_login(
    message: Message, response: tuple, text: str
        ):
    con, cursor = db_open()
    if response[1] == 'Idle':
        db_close(con)
        await message.answer('Сначала выберите команду /add или /del')
    elif response[1] == 'Add':
        cursor.execute(
            'SELECT task FROM public.table WHERE user_id = %s and task = %s', (
                message.from_user.id, text)
        )
        task = cursor.fetchone()
        if task:
            db_close(con)
            await message.answer('Задача уже есть в базе. Для просмотра \
задач выбери команду /get.')
        else:
            cursor.execute('INSERT INTO public.table(user_id, task) \
                    VALUES (%s, %s)', (
                message.from_user.id, text
                )
            )
            db_close(con)
    elif response[1] == 'Del':
        cursor.execute(
            "SELECT task FROM public.table WHERE user_id = %s and \
                task ILIKE %s", (
                    message.from_user.id, f'%{text}%',)
        )
        task = cursor.fetchone()
        if task:
            cursor.execute('DELETE FROM public.table \
                    WHERE task ILIKE %s', (
                        f'%{text}%',
                )
            )
            db_close(con)
        else:
            db_close(con)
            await message.answer('Задачи нет в базе. Для просмотра \
задач выбери команду /get.')


@dp.message(TextFilter())
async def process_text_messages(message: Message):
    await message.answer('Не нахожу тебя в своей базе, нажми /start, \
чтобы авторизоваться.')


@dp.message()
async def process_other_messages(message: Message):
    await message.answer('Я не могу реагировать на такие запросы, \
                        пожалуйста, введи текст')


if __name__ == '__main__':
    dp.run_polling(bot)
