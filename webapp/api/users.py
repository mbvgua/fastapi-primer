"""
these endpoints return data in JSON format. basic data aimed at giving general
overview of what the application does.

also these endpoints are what is included in the OpenApi documentation in:
    - https:127.0.0.1:8000/docs
    - https:127.0.0.1:8000/redoc

endpoints included here are:
    * CREATE:
        - /api/users
    * READ(GET):
        - /api/users
        - /api/users/{user_id}
        - /api/users/{user_id}/posts
    * UPDATE:
        - PUT:
        - PATCH: /api/users/{user_id}
    * DELETE:
        - /api/users/{user_id}
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from webapp.database import models
from webapp.database.config import get_db
from webapp.schemas.users import UserCreate, UserResponse, UserUpdate
from webapp.schemas.posts import PostResponse

router = APIRouter(prefix="/api/users")


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """
    documentation endpoint for creating new users into the program

    it uses the UserCreate schema for validation all inputs, the through
    dependecy injection, creates the databse connection, and returns those
    results as the db parameter.
    """
    # check to see if user already exists
    data = db.execute(
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
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    documentation endpoint for getting a user from the program

    it uses the UserResponse schema for validation all inputs, the through
    dependecy injection, creates the databse connection, and returns those
    results as the db parameter.
    """
    data = db.execute(select(models.User).where(models.User.id == user_id))

    # NOTE: try getting only the .scalar() value and see the difference
    existing_user = data.scalars().first()

    # fail first, fail cleanly
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! looks like the user does not exist, try again?",
        )

    return existing_user


@router.get("/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    documentation endpoint to get all posts uploaded by a given user
    """

    data = db.execute(select(models.User).where(models.User.id == user_id))
    existing_user = data.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! Looks like the user does not exist, try again?",
        )

    data = db.execute(
        select(models.Post).where(models.Post.user_id == existing_user.id)
    )
    posts = data.scalars().all()
    return posts


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, updated_user: UserUpdate, db: Annotated[Session, Depends(get_db)]
):
    """
    documentation endpoint that updates a users values
    """
    data = db.execute(select(models.User).where(models.User.id == user_id))
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
        data = db.execute(
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

    db.commit()
    db.refresh(existing_user)
    return existing_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    documentation endpoint to deletea user from the application using their id

    does not return anything, but if successful, the response status code is
    204, which means content has successfully been deleted
    """
    data = db.execute(select(models.User).where(models.User.id == user_id))
    existing_user = data.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oh no! Looks like the user does not exist. Try again?",
        )

    db.delete(existing_user)
    db.commit()
