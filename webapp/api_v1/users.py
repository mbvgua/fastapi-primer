"""
contain routes for the "/api/users" endpoints. they return data in JSON format

also these endpoints are what is included in the OpenAPI documentation in:
    - https:127.0.0.1:8000/docs
    - https:127.0.0.1:8000/redoc

endpoints included here are:
    * CREATE:
        - /api/users: create_user
    * READ(GET):
        - /api/users/{user_id}: get_user_by_id
        - /api/users/{user_id}/posts: get_user_posts_by_id
    * UPDATE(PATCH):
        - /api/users/{user_id}: update_user
    * DELETE:
        - /api/users/{user_id}: delete_user_by_id
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from webapp.database import models
from webapp.database.config import get_db
from webapp.schemas.users import (
    UserCreate,
    UserPrivateResponse,
    UserPublicResponse,
    UserUpdate,
)
from webapp.schemas.posts import PostResponse
from webapp.utils.auth import get_current_user
from webapp.utils.passwords import PasswordUtils

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post(
    "", response_model=UserPrivateResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    "/api/users"
    creates new user in the application.

    it uses the "UserCreate" schema for validation of all inputs. through
    dependecy injection it creates the database connection, and returns those
    results as the db parameter.

    NOTE:
    - "func.lower()": makes the database value fetched to be in lowercase.
      using this alongside the ".lower()" method for the string being compared
      against allows for case-insensitive searching.
    """
    # case-insensitive check to see if user already exists
    data = await db.execute(
        select(models.User).where(
            func.lower(models.User.username) == user.username.lower()
            or func.lower(models.User.email) == user.email.lower()
        )
    )
    existing_user = data.scalars().first()

    # checks if there is an existing user, and raises a HTTP exception
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists. Try again?",
        )

    # if not add user to the db
    new_user = models.User(
        username=user.username,
        email=user.email.lower(),
        password_hash=PasswordUtils.hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user_by_id(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    "/api/users/{user_id}"
    get a users data, based on the "user_id" passed in.

    it uses the "UserPublicResponse" schema for validation all inputs, the through
    dependecy injection, creates the database connection, and returns those
    results as the db parameter.
    """
    data = await db.execute(select(models.User).where(models.User.id == user_id))
    existing_user = data.scalars().first()

    # fail first, fail cleanly
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! looks like the user does not exist, try again?",
        )

    return existing_user


@router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts_by_id(
    user_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    "/api/users/{user_id}/posts"
    get all posts uploaded by a given user, filtering by the "user_id" passed
    in.

    NOTE:
    - "order_by()": orders the posts, ensuring the most recent appear first
    - "selectinload()": allows for eargely loading in the async sqlite session,
      hence the request is able to access "models.Post.author", lest it would
      return and error
    """

    data = await db.execute(select(models.User).where(models.User.id == user_id))
    existing_user = data.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! Looks like the user does not exist, try again?",
        )

    data = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == existing_user.id)
        .order_by(models.Post.date_posted.desc())
    )
    posts = data.scalars().all()
    return posts


@router.patch("/{user_id}", response_model=UserPrivateResponse)
async def update_user(
    user_id: int,
    updated_user: UserUpdate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    "/api/users/{user_id}"
    updates a users information, based on the "user_id" passed in as a parameter
    uses the "patch" protocol. all fields are optional for this update.
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Oh no! Looks like you are not authorized to update this user.",
        )

    data = await db.execute(select(models.User).where(models.User.id == user_id))
    existing_user = data.scalars().first()

    # if users does not exist, fail cleanly
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oh no! User does not exist. Try again?",
        )

    # if user tried to update their email or username, ensure it does not exist
    # in the application to make it unique
    if (
        updated_user.username is not None
        and updated_user.username != existing_user.username
        and updated_user.email is not None
        and updated_user.email != existing_user.email
    ):
        # case-insensitive check to see if user already exists
        data = await db.execute(
            select(models.User).where(
                func.lower(models.User.username) == updated_user.username.lower()
                or func.lower(models.User.email) == updated_user.email.lower()
            )
        )
        existing_username_or_email = data.scalars().first()

        if existing_username_or_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or Username is taken! Try again?",
            )

    # overwrites only the data fields passed in by the user, and not update all
    # of them, as those maybe become the default value('None')
    # .model_dump returns a dictionary
    updated_data = updated_user.model_dump(exclude_unset=True)

    for field, value in updated_data.items():
        setattr(existing_user, field, value)

    await db.commit()
    await db.refresh(existing_user)
    return existing_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: int,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    "/api/users/{user_id}"
    endpoint to delete user from the application using the "user_id" passed in.

    does not return any response data, but if successful, the response status code is
    204, which means action has successfully been performed, which in this case
    means user account has been deleted.
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Oh no! Looks like you are not authorized to delete this user.",
        )

    data = await db.execute(select(models.User).where(models.User.id == user_id))
    existing_user = data.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oh no! Looks like the user does not exist. Try again?",
        )

    await db.delete(existing_user)
    await db.commit()
