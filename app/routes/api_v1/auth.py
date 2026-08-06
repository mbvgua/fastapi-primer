"""
contains routes for the "/api/auth" endpoints.

these routes will be included in the OpenAPI documentation in:
    - https:127.0.0.1:8000/docs
    - https:127.0.0.1:8000/redoc

endpoints included here are:
    * CREATE:
    * READ(GET):
        - /api/auth/login: login_for_access_token
        - /api/auth/me: get_current_user
    * UPDATE:
    * DELETE:
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import models
from app.database.config import get_db
from app.schemas.users import (
    UserPrivateResponse,
    UserTokenResponse,
)
from app.utils.auth import get_current_user
from app.utils.passwords import PasswordUtils
from app.utils.tokens import TokenUtils

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/token", response_model=UserTokenResponse)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    endpoint for assigning tokens to users logging in to the application.

    the "form_data" is parsed by the "OAuth2PasswordRequestForm", which is
    injected as a dependecy. it parses the form for the "username" and
    "password" fields, normally used in OAuth2 validation.

    also through dependecy injection, it creates the database connection, and
    returns those results as the db parameter.

    NOTE:
    - "func.lower()": makes the database value fetched to be in lowercase.
      using this alongside the ".lower()" method for the string being compared
      against allows for case-insensitive searching.
    """
    data = await db.execute(
        select(models.User).where(
            func.lower(models.User.username) == form_data.username.lower()
        )
    )
    existing_user = data.scalars().first()

    # if user does not exists, or paswords dont match fail cleanly
    if not existing_user or not PasswordUtils.verify_password(
        form_data.password, existing_user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password. Try again?",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # create token, using "user_id" as sub
    access_token = TokenUtils.create_access_token(data={"sub": str(existing_user.id)})

    return UserTokenResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserPrivateResponse)
async def current_user(
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    """
    endpoint to decode and validate user token. the latter is an essential
    reason as to why we have not implemented this in functionality as an inline
    Js script

    if token is valid, it returns the users data, utilising the
    "UserPrivateResponse" schema.
    """

    return current_user
