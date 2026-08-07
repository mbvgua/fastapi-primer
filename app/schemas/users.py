"""
pydantic validation schemas which help define the shape of the data present in
the application. it also helps validate schemas, preventing api access until
all required fields are inputted.

below are validation schemas for the users model. they include:
    - UserBase
    - UserCreate
    - UserPublicResponse
    - UserPrivateResponse

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

    # FIXME: how do I ensure password is alphanumeric?
    password: str = Field(min_length=8)


class UserPublicResponse(BaseModel):
    """
    inherits from BaseModel. used for frontend facing scenarios, where security
    of users data is not essential. to ensure this, the email and password are
    not displayed here. adds the following fields:
    - id
    - username
    - image_file
    - image_path    -> auto-generated if 'image_file' is None
    """

    # use pydantic to read from SqlAlchemy models and properties using
    # dot-notation
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str


class UserPrivateResponse(UserPublicResponse):
    """
    inherits from UserPublicResponse. used for backend operations where user
    data security is essential. e.g where a user needs to verify their own
    data, say update their profile, hence emails and password can be passed.

    adds the following fields:
    - email:str
    """

    # use pydantic to read from SqlAlchemy models and properties using
    # dot-notation
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr


class UserUpdate(BaseModel):
    """
    inherits from the BaseModel, since its an update, it makes all fields
    optional. If it were to inherit from the UserBase schema, it would mean
    overwriting them, which causes errors.

    NOTE:
    - since the inputs are optional, they have to have a 'default' value
    - we do not include the 'id' value for update as that would change
      ownership of the posts
    - not handle "image_file" updates, as there are dedicated routes that
      handle that entirely, with appropriate validation and auth
    """

    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)


class UserTokenResponse(BaseModel):
    """
    inherits from the BaseModel. used to define how the token will be shaped
    like. it contains:
    - access_token: str
    - token_type: str
    """

    access_token: str
    token_type: str
