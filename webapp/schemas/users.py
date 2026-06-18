"""
pydantic schemas help prevent exposing data that should not bee seen by all.
it also helps validate schemas, preventing api access until all required fields
are inputted.

below are validation schemas for the users model. they include:
    - UserBase
    - UserCreate
    - UserResponse

these schemas are enforced by fastapi and generated automaticaly in the docs
"""

from pydantic import BaseModel, ConfigDict, Field, EmailStr


# validation schemas for Users
class UserBase(BaseModel):
    """
    schema for datafields to be shared between the UserCreate & UserResponse
    schemas
    """

    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=100)


class UserCreate(UserBase):
    """
    inherits from UserBase above
    """

    pass


class UserResponse(UserBase):
    """
    inherits from UserBase

    adds 'id', 'image_file' & 'image_path'
    """

    # allows pydantic to read from SqlAlchemy models and properties
    model_config = ConfigDict(from_attributes=True)  # allow using dot-notation

    id: int
    image_file: str | None
    image_path: str
