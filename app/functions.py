from datetime import datetime, UTC
from typing import Literal

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from psycopg2.extras import RealDictCursor

from models import Task, DbConnect


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


async def get_tasks(id: int, status: Literal['outdated', 'current'],
                    order: str) -> None | list:
    status = 'target_date >= now()::DATE' if status == 'current' \
        else 'target_date < now()::DATE'
    with DbConnect() as db:
        db.cur.execute('''SELECT id, task,
                       target_date, task_status
                       FROM task
                       WHERE {status} and user_id=%s
                       ORDER BY target_date {order}'''.format(status=status,
                                                              order=order),
                       (id, ))
        validated_data = [Task(**ele) for ele in db.cur.fetchall()]
        return validated_data


async def start(id: int, name: str) -> None:

    with DbConnect() as db:
        db.cur.execute('SELECT id, modified FROM users WHERE id=%s', (id,))
        response = db.cur.fetchone()
        if not response:
            db.cur.execute('INSERT INTO users (id, name) VALUES (%s, %s)',
                           (id, name))
        else:
            time_delta = datetime.now(tz=UTC) - response['modified']
            if time_delta.days > 1:
                db.cur.execute('''UPDATE users SET name = %s
                               WHERE id = %s''', (name, id))


async def add_task(id: int, task: str, date: str) -> None:
    date = datetime.strptime(date, '%Y/%m/%d')
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
