import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase



SQL_ALCHEMY_DATABASE_URL = os.getenv('SQL_ALCHEMY_DATABASE_URL')

if SQL_ALCHEMY_DATABASE_URL is None:
    raise ValueError('SQL_ALCHEMY_DATABASE_URL environment variable is not set')


async_engine = create_async_engine(SQL_ALCHEMY_DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass
