from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# tell slqlite where to connect
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # sqlite is single threaded. fastAPI can handle requests asynchronously
    # this enables this feature for better performance
    connect_args={"check_same_thread": False},
)

# create transcations pools with the db
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    provide sessions to our routes. fastAPI will reference this
    function(through dependency injection) for each request, ensuring that it
    each request has its own session, in which cleanup happens automatically
    """
    with session_local() as db:
        yield db
