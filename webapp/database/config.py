"""
asynchronous database connection

this allows our program to handle multiple concurrent requests. as compared to
syncronous programs where one thing happens after another. aysnc helps avoid
the wait for common I/O bound tasks, such as a database response, network
response or a file to read. instead, other work will be performed.

NOTE:
- all the above tasks are involved with waiting tasks, and not computing.
  these are CPU bound operations, such as data crunching, heavy calculations,
  graphics rendering, which all keep the CPU engaged with actual work, there
  is no waiting involved here, hence making such application async would not
  help in any way. asynchronous really shine when our programs need to handle
  lots of concurrent loads(multiple request at the same time), which can be
  said to be the default of most webapps today
- async...await has been a common feature in the javascript/typescript ecosystem

"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# tell slqlite where to connect
# +aiosqlite tells to which asynchronous driver
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    # sqlite is single threaded. fastAPI can handle requests asynchronously
    connect_args={"check_same_thread": False},
)

# create transcations pools with the db
async_session_local = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """
    provide sessions to our routes. fastAPI will reference this
    function(through dependency injection) for each request, ensuring that it
    each request has its own session, in which cleanup happens automatically
    """
    async with async_session_local() as db:
        yield db
