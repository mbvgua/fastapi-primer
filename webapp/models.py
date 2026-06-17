"""
this file defines our database tables using SQLAlchemy ORM(Object Relational
Mapping)

TODO: make plain'ol tables with SQL. see if it works!
"""

from __future__ import annotations
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
