from datetime import datetime, UTC

from aiogram.utils.keyboard import InlineKeyboardBuilder
from psycopg2.extras import RealDictCursor

from models import Task, DbConnect


def set_schema(cur: RealDictCursor):
    '''Set search path for easier table appeal'''
    cur.execute('SET search_path TO content,public')


async def prepare_list_of_task(lst: list, ) -> str:

    validated_data = [Task(**ele) for ele in lst]
    res = ''
    for j, ele in enumerate(validated_data):
        date = ele.target_date.strftime("%d_%m_%Y")
        res += f'<b>{date}:</b>\n\n'
        for i, val in enumerate(ele.tasks):
            if ele.status[i] == 'active':
                s = f"{i+1}. {val}"
            else:
                s = f"<strike>{i+1}. {val}</strike>"
            if i == len(ele.tasks)-1:
                s += '.\n'
            else:
                s += ';\n'
            res += s
        if j != len(validated_data)-1:
            res += '\n'
    return res


async def get_current_tasks(id: int) -> None | list:
    with DbConnect() as db:
        db.cur.execute('''SELECT array_agg(task) as tasks, \
                       target_date, array_agg(task_status) as status
                       FROM task
                       WHERE target_date >= now()::DATE and user_id=%s
                       GROUP BY target_date
                       ORDER BY target_date''', (id,))
        return db.cur.fetchall()


async def get_outdated_tasks(id: int) -> None | list:
    with DbConnect() as db:
        db.cur.execute('''SELECT array_agg(task) as tasks, \
                       target_date, array_agg(task_status) as status
                       FROM task
                       WHERE target_date < now()::DATE and user_id=%s
                       GROUP BY target_date
                       ORDER BY target_date DESC''', (id,))
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


async def create_tasks_list_for_mark(lst: list):
    builder = InlineKeyboardBuilder()
    validated_data = [Task(**ele) for ele in lst]
    for i, ele in enumerate(lst):
        builder.button(text=ele, callback_data=f"{i}")
    builder.button(text='Все категории', callback_data=f"{len(lst)}")
    builder.adjust(3, 1)
    return builder
