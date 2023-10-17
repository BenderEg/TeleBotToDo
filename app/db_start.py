from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from settings import settings


Base = declarative_base(name='content')

dsn = f'''postgresql+asyncpg://{
    settings.postgres_user}:{settings.postgres_password}@{
        settings.host}:{settings.port_db}/{settings.postgres_db}'''
engine = create_async_engine(dsn, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession,
                             expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
