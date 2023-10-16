from datetime import datetime, UTC

from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from psycopg2.extras import RealDictCursor

from db_models import User, Task
from db_start import get_session
from models import Task, DbConnect

async def set_main_menu(bot: Bot):

    main_menu_commands = [
        BotCommand(command='/get_current',
                   description='Вывод текузщих задач'),
        BotCommand(command='/get_outdated',
                   description='Вывод задач за прошедшую неделю'),
        BotCommand(command='/mark_done',
                   description='Пометить задачу как выполненную'),
        BotCommand(command='/add',
                   description='Добавить задачу'),
        BotCommand(command='/calendar',
                   description='Календарь и выбор даты'),
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/cancel',
                   description='Для выхода из режима'),
        BotCommand(command='/start',
                   description='Для старта работы'),
            ]
    await bot.set_my_commands(main_menu_commands)


def set_schema(cur: RealDictCursor):
    '''Set search path for easier table appeal'''
    cur.execute('SET search_path TO content,public')


async def prepare_list_of_task(lst: list[Task]) -> str:

    res = ''
    d = {}
    for ele in lst:
        if ele.target_date not in d:
            d[ele.target_date] = [(ele.task, ele.task_status)]
        else:
            d[ele.target_date].append((ele.task, ele.task_status))
    for ele in d.keys():
        date = ele.strftime("%d_%m_%Y")
        res += f'<b>{date}:</b>\n\n'
        for i, val in enumerate(d[ele], 1):
            if val[1] == 'active':
                s = f"{i}. {val[0]}"
            else:
                s = f"<strike>{i}. {val[0]}</strike>"
            if i == len(d[ele]):
                s += '.\n\n'
            else:
                s += ';\n'
            res += s
    return res


async def filter_active_task(lst: list[Task]) -> list:

    return list(filter(lambda x: x.task_status == 'active', lst))


async def filter_inactive_task(lst: list[Task]) -> list:

    return list(filter(lambda x: x.task_status == 'inactive', lst))


async def filter_current_task(lst: list[Task]) -> list:

    return list(filter(lambda x: x.target_date >= datetime.now().date(), lst))


async def filter_outdated_task(lst: list[Task]) -> list:

    return list(filter(lambda x: x.target_date < datetime.now().date(), lst))


async def filter_mark_done_task(lst: list[Task]) -> list:

    return list(filter(
        lambda x: (x.target_date - datetime.now().date()).days >= -2, lst)
        )


async def get_tasks(id: int,
                    order: str) -> None | list:
    with DbConnect() as db:
        db.cur.execute('''SELECT id, task,
                       target_date, task_status
                       FROM task
                       WHERE user_id=%s
                       ORDER BY target_date {order}'''.format(
                           order=order),
                       (id, ))
        validated_data = [Task(**ele) for ele in db.cur.fetchall()]
        return validated_data


async def start(id: int, name: str) -> None:

    session: AsyncSession = await anext(get_session())
    result = await session.get(User, id)
    if not result:
        await session.add(User(name=name))
    else:
        time_delta = datetime.now(tz=UTC) - result.modified
        if time_delta.days >= 1:
            result.name = name
            result.modified = datetime.now(tz=UTC)
    await session.commit()


async def add_task(id: int, task: str, date: str) -> None:
    date = datetime.strptime(date, '%Y_%m_%d')
    with DbConnect() as db:
        db.cur.execute('''INSERT into task
                       (user_id, task, target_date)
                       VALUES (%s, %s, %s)
                       ON CONFLICT (user_id, task, target_date)
                       DO NOTHING''', (id, task, date))


async def update_mark_task(id: int, state: FSMContext) -> None:
    data: dict = await state.get_data()
    if data and data['marked_tasks']:
        with DbConnect() as db:
            db.cur.executemany('''UPDATE task
                               SET task_status = 'inactive'
                               WHERE user_id = %s
                               AND id = %s''', ((id, ele)
                                                for ele in data[
                                                    'marked_tasks']))
    await state.clear()


async def create_tasks_list_for_mark(lst: list[Task], state: FSMContext):
    tasks_dict = {ele.id: [ele.target_date.strftime('%Y_%m_%d'), ele.task]
                  for ele in lst if ele.task_status == 'active'}
    await state.update_data(tasks_dict=tasks_dict, marked_tasks=[])
    builder = await create_tasks_builder(tasks_dict)
    return builder


async def create_tasks_builder(d: dict) -> InlineKeyboardBuilder:

    builder = InlineKeyboardBuilder()
    for key, value in d.items():
        builder.button(text=f'{value[0]}: {value[1]}',
                       callback_data=f"{key}")
    builder.adjust(1, 1)
    return builder