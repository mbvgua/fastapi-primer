"""
this file defines our database tables using SQLAlchemy ORM(Object Relational
Mapping)

if you're on an older Python version, lower than 3.14, you'd need to place
` from __future__ import annotations` at the top of your imports to allow
Python to perform forward-referencing of Posts table from the Users table, i.e
referencing a table before it is created. this is now default in Python >=3.14.

this is similar to sth called hoisting in javascript ecosystem

TODO: make plain'ol tables with SQL. see if it works!
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.database import Base


class User(Base):
    """
    this is the default user table. it inherits from the 'Base'model in database.py

    Mapped: allows for type hints in our IDE

    using 'relationship' for the 'posts' column created a one-to-many relationship
    where one user can have multiple posts
    'back_populates' links to the 'author' column in Posts
    """

    # define table name. good practise to be in plural
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    image_file: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None
    )

    # NOTE: we reference the 'Post' table before its created.
    # this is called forward-referencing
    posts: Mapped[list[Post]] = relationship(back_populates="author")

    @property
    def image_path(self) -> str:
        """
        decorator ensures that if a user *does* upload an image, that is what
        is returned. if not, it returns the default image, that is used by all
        who have'nt uploaded an image

        separating the /static(media shipped with our application) and the /media
        (madia uploaded by users) directories, it helps to have a clear
        division, this makes other operations such as backups & deployments
        much easier
        """
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"

        return "/static/profile_pics/default.jpg"


class Post(Base):
    """
    creates the posts table
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
    author: Mapped[User] = relationship(back_populates="posts")
