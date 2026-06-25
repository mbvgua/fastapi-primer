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
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from webapp.database import models
from webapp.database.config import get_db
from webapp.schemas.users import UserCreate, UserResponse, UserUpdate
from webapp.schemas.posts import PostResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    endpoint for creating new users into the program

    it uses the "UserCreate" schema for validation all inputs, through
    dependecy injection, creates the database connection, and returns those
    results as the db parameter.
    """
    # check to see if user already exists
    data = await db.execute(
        select(models.User).where(
            models.User.username == user.username or models.User.email == user.email
        )
    )
    # check the first user object or None if no match
    existing_user = data.scalars().first()

    # checks if there is an existing user, and raises a HTTP exception
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists, try again?",
        )

    # if not add user to the db
    new_user = models.User(username=user.username, email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    endpoint for getting a user filtering by their "user_id"

    it uses the "UserResponse" schema for validation all inputs, the through
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
    endpoint to get all posts uploaded by a given user, filtering by the
    "user_id"

    NOTE:
    - "order_by()": orders the posts, ensuring the most recent appear first
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


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, updated_user: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    endpoint that updates a users information, baased on the "user_id" passed
    in as a parameter.
    """
    data = await db.execute(select(models.User).where(models.User.id == user_id))
    existing_user = data.scalars().first()

    # if users does not exist, fail cleanly
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oh no! User not found, try again?",
        )

    # if user tried to update their email or username, ensure it does not exist
    # in the application to make it unique
    if (
        updated_user.username is not None
        and updated_user.username != existing_user.username
        and updated_user.email is not None
        and updated_user.email != existing_user.email
    ):
        data = await db.execute(
            select(models.User).where(
                models.User.username == updated_user.username
                or models.User.email == updated_user.email
            )
        )
        existing_username_or_email = data.scalars().first()

        if existing_username_or_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or Username is taken! try again?",
            )

    # overwrites only the data fields passed in by the user, and not update all
    # of them, as those maybe become what is set as default ->'None'
    updated_data = updated_user.model_dump(exclude_unset=True)

    # .model_dump returns a dictionary
    for field, value in updated_data.items():
        setattr(existing_user, field, value)

    await db.commit()
    await db.refresh(existing_user)
    return existing_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    endpoint to delete user from the application using their "user_id"

    does not return anything, but if successful, the response status code is
    204, which means content has successfully been deleted
    """
    data = await db.execute(select(models.User).where(models.User.id == user_id))
    existing_user = data.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oh no! Looks like the user does not exist. Try again?",
        )

    await db.delete(existing_user)
    await db.commit()
