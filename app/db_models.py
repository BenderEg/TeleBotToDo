import uuid

from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from db_start import Base


class User(Base):

    __tablename__ = 'users'

    id = Column(name='id', primary_key=True, nullable=False,
                type_=Integer, default=uuid.uuid4, unique=True)
    name = Column(name='name', type_=String(length=100), nullable=False)
    created = Column(name='created', type_=DateTime(),
                     default=datetime.utcnow())
    modified = Column(name='modified', type_=DateTime(),
                      default=datetime.utcnow())

    def __init__(self, name: str) -> None:
        self.name = name


class Task(Base):

    __tablename__ = 'task'

    id = Column(name='id', primary_key=True, nullable=False,
                type_=UUID(as_uuid=True), default=uuid.uuid4,
                unique=True)
    user_id = Column('user_id', ForeignKey('users.id'),
                     nullable=False)
    task = Column(name='task', type_=String, nullable=False)
    target_date = Column(name='target_date', type_=DateTime(),
                         default=datetime.utcnow().date())
    created = Column(name='created', type_=DateTime(),
                     default=datetime.utcnow())
    modified = Column(name='modified', type_=DateTime(),
                      default=datetime.utcnow())
    task_status = Column(name='task_status',
                         type_=String, nullable=False,
                         default='active')

    def __init__(self, user_id: uuid.UUID, task: str,
                 target_date: datetime) -> None:
        self.name = user_id
        self.name = task
        self.name = target_date
