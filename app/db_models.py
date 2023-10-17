import uuid

from datetime import datetime, UTC

from sqlalchemy import Column, String, Integer, \
    Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from db_start import Base


class User(Base):

    __tablename__ = 'users'

    id = Column(name='id', primary_key=True, nullable=False,
                type_=Integer, unique=True)
    name = Column(name='name', type_=String(length=100), nullable=False)
    created = Column(name='created', type_=DateTime(timezone=True),
                     default=datetime.now(tz=UTC),
                     nullable=False)
    modified = Column(name='modified', type_=DateTime(timezone=True),
                      default=datetime.now(tz=UTC),
                      nullable=False)

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name


class Task(Base):

    __tablename__ = 'task'

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
                     default=datetime.now(tz=UTC))
    modified = Column(name='modified', type_=DateTime(timezone=True),
                      default=datetime.now(tz=UTC))
    task_status = Column(name='task_status',
                         type_=String, nullable=False,
                         default='active')

    def __init__(self, user_id: uuid.UUID, task: str,
                 target_date: datetime) -> None:
        self.user_id = user_id
        self.task = task
        self.target_date = target_date
