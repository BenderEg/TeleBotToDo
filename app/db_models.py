import uuid

from datetime import datetime, UTC

from sqlalchemy import Column, String, Integer, \
    Date, DateTime, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects import postgresql

from db_start import Base


class User(Base):

    __tablename__ = 'users'

    id = Column(name='id', primary_key=True, nullable=False,
                type_=Integer, unique=True)
    name = Column(name='name', type_=String(length=100), nullable=False)
    created = Column(name='created', type_=DateTime(timezone=True),
                     default=datetime.now(tz=UTC),
                     nullable=False)
    modified = Column(name='modified', type_=TIMESTAMP(timezone=True),
                      onupdate=func.now(),
                      server_default=text('now()'),
                      nullable=False)

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name


class Task(Base):

    __tablename__ = 'task'
    __table_args__ = (UniqueConstraint('user_id', 'task', 'target_date'), )

    id = Column(name='id', primary_key=True, nullable=False,
                type_=UUID(as_uuid=True), default=uuid.uuid4,
                unique=True)
    user_id = Column('user_id', ForeignKey(User.id),
                     nullable=False)
    task = Column(name='task', type_=String, nullable=False)
    target_date = Column(name='target_date', type_=Date(),
                         default=datetime.today(),
                         nullable=False)
    created = Column(name='created', type_=DateTime(timezone=True),
                     default=datetime.now(tz=UTC),
                     nullable=False)
    modified = Column(name='modified', type_=TIMESTAMP(timezone=True),
                      onupdate=func.now(),
                      server_default=text('now()'),
                      nullable=False)
    task_status = Column(name='task_status',
                         type_=String, nullable=False,
                         default='active')

    def __init__(self, user_id: uuid.UUID, task: str,
                 target_date: datetime) -> None:
        self.user_id = user_id
        self.task = task
        self.target_date = target_date

    @staticmethod
    async def upsert_values(db: AsyncSession, values: dict):
        stmt = postgresql.insert(Task).values(**values)
        await db.execute(stmt.on_conflict_do_update(
            constraint='task_user_id_task_target_date_key',
            set_={'task_status': 'active'}))
        await db.commit()
