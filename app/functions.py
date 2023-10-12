from datetime import datetime, UTC

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from psycopg2.extras import RealDictCursor

from models import Task, DbConnect


def set_schema(cur: RealDictCursor):
    '''Set search path for easier table appeal'''
    cur.execute('SET search_path TO content,public')


async def prepare_list_of_task(lst: list, ) -> str:

    validated_data = [Task(**ele) for ele in lst]
    res = ''
    d = {}
    for ele in validated_data:
        if ele.target_date not in d:
            d[ele.target_date] = [(ele.task, ele.task_status)]
        else:
            d[ele.target_date].append((ele.task, ele.task_status))
    for j, ele in enumerate(d.keys()):
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


async def get_tasks(id: int, order: str) -> None | list:
    with DbConnect() as db:

        db.cur.execute('''SELECT id, task,
                       target_date, task_status
                       FROM task
                       WHERE target_date >= now()::DATE and user_id=%s
                       ORDER BY target_date {order}'''.format(order=order),
                       (id, ))
        return db.cur.fetchall()


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


async def create_tasks_list_for_mark(lst: list, state: FSMContext):
    validated_data = [Task(**ele) for ele in lst]
    tasks_list = []
    for ele in validated_data:
        for value in ele.tasks:
            tasks_list.append([ele.target_date.strftime('%Y_%m_%d'), value])
    await state.update_data(tasks_list=tasks_list, marked_tasks=[])
    builder = await create_tasks_builder(tasks_list)
    return builder


async def create_tasks_builder(lst: list) -> InlineKeyboardBuilder:

    builder = InlineKeyboardBuilder()
    for i, ele in enumerate(lst):
        builder.button(text=f'{ele[0]}: {ele[1]}',
                       callback_data=f"{i}")
    builder.adjust(1, 1)
    return builder
