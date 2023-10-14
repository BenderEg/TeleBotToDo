from contextlib import closing
from os import environ

import psycopg2

from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


def delete_old_tasks(cur: RealDictCursor, days: int):
    cur.execute('''DELETE from task
                WHERE (now()::DATE - target_date) > %s''',
                (days,))


if __name__ == '__main__':
    dsl = {'dbname': environ.get('POSTGRES_DB'),
           'user': environ.get('POSTGRES_USER'),
           'password': environ.get('POSTGRES_PASSWORD'),
           'host': environ.get('HOST'),
           'port': environ.get('PORT_DB')}
    with closing(psycopg2.connect(
            **dsl, cursor_factory=RealDictCursor)) as pg_conn:
        with pg_conn.cursor() as cur:
            delete_old_tasks(cur, environ.get('DAYS'))
            pg_conn.commit()
