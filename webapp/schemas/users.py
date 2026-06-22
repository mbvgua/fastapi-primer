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


class UserBase(BaseModel):
    """
    the main base schema. this contains data fields that are shared between
    the UserCreate and UserResponse schemas.
    """

    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=100)


class UserCreate(UserBase):
    """
    inherits from UserBase schema
    """

    pass


class UserResponse(UserBase):
    """
    inherits from UserBase. adds the following fields:
    - id
    - image_file
    - image_path    -> auto-generated if 'image_file' is None
    """

    # allows pydantic to read from SqlAlchemy models and properties
    model_config = ConfigDict(from_attributes=True)  # allow using dot-notation

    id: int
    image_file: str | None
    image_path: str


class UserUpdate(BaseModel):
    """
    inherits from the BaseModel, since its an update, it makes all fields
    optional. If it were to inherit from the UserBase schema, it would mean
    overwriting them, which causes errors.

    NOTE:
    - since the inputs are optional, they have to have a 'default' value
    - we do not include the 'id' value for update as that would change
      ownership of the posts
    """

    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    image_file: str | None = Field(default=None, min_length=1)
