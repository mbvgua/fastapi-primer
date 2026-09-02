"""
define our database tables using SQLAlchemy ORM(Object Relational Mapping)

if you're on an older Python version, <3.14, you'd need to place
`from __future__ import annotations` at the top of your imports to allow
Python to perform forward-referencing of Posts table from the Users table, i.e
referencing a table before it is created. this is now default in Python >=3.14.

this is similar to hoisting in javascript ecosystem
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base
from app.config import settings


class User(Base):
    """
    creates the 'users' table. It inherits from the 'Base' class found in the
    database.config.py file.

    the table contains the following columns:
        * id:str    -> primary_key
        * username:str
        * email:str
        * password_hash:str
        * image_file:str|None
        * image_path:str|None
        * posts: list[Post]
        * reset_tokens: list[PasswordResetToken]

    NOTE:
    - using 'Mapped' in the column definitons allows for type hints in our IDE
    - using 'relationship' for the 'posts' column created a one-to-many relationship
      where one user can have multiple posts
    - 'back_populates' links to the 'author' column in Posts, allowing one to
      perform operations like 'user.posts.[id, title, content, date_posted]
    """

    # define table name. good practise to be in plural
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(300), nullable=False)
    image_file: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None
    )
    # NOTE: we reference the 'Post' table before its created. this is called forward-referencing
    posts: Mapped[list[Post]] = relationship(
        back_populates="author",
        # NOTE: deletes user alongside all of their posts. FastAPI does
        # this by default, so this is just a precaution for older versions.
        # TODO: Also, change it from cascade into making all deleted posts belong to
        # a "ghost" user, like github, reddit e.t.c
        cascade="all, delete-orphan",
    )
    reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def image_path(self) -> str:
        """
        decorator ensures that if a user *does* upload an image, that is what
        is returned. if not, it returns the default image, that is used by all
        who have not uploaded an image

        separating the "/static" (media shipped with our application) and the
        "/media" (media uploaded by users) directories, it helps to have a
        clear division, this makes other operations such as backups &
        deployments much easier
        """
        if self.image_file:
            return f"https://{settings.s3_bucket_name}.s3.{settings.s3_region}.amazonaws.com/profile_pics/{self.image_file}"

        return "/static/profile_pics/default.jpg"


class Post(Base):
    """
    creates the 'posts' table. It inherits from the 'Base' class found in the
    database.config.py file.

    the table contains the following columns:
        * id:str    -> primary_key
        * title:str
        * content:str
        * user_id:int   -> foreign_key
        * date_posted:datetime
        * author:User

    NOTE:
    - using 'Mapped' in the column definitons allows for type hints in our IDE
    - using 'relationship' for the 'author' column created a one-to-many relationship
      where one user can have multiple posts
    - 'back_populates' links to the 'posts' column in Users, allowing one to
      perform operations like 'post.author.[username, email, id, image_file]'
    - in likes column, "server_default" was used to prevent the database from
      inputting "null" in the existing columns. as I was testing migrations
      later on, this column did not exist initially as thetable was created.,
      using this better than manually editing the miggration files later on.
    """

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    likes: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    author: Mapped[User] = relationship(back_populates="posts")


class PasswordResetToken(Base):
    """
    creates the 'password_reset_tokens' table. It inherits from the 'Base' class
    found in the database.config.py file.

    the table contains the following columns:
        * id:str    -> primary_key
        * user_id   -> foreign_key
        * token_hash:str
        * expires_at:datetime
        * created_at:datetime
        * user:User

    NOTE:
    - this stores our password reset tokens. we have not used our JSONWebTokens
      for this since we need to have randomn single-use tokens that are stored
      securely. JWTs cannot be invalidated before they expire, unless one
      maintains a blacklist in the database. This no longer makes them secure.
      with database stored tokens, we get a true single use behaviour by
      deleting the token after successful resets. and we can invalidate them at
      anytime.
    - token_hash: only stores the hash, not the actual token. in the event of a
      database leak, only the hash is leaked, and these are useless without the
      actual token
    """

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    user: Mapped[User] = relationship(back_populates="reset_tokens")
