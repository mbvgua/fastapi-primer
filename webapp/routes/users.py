"""
contains routes for the /users endpoints. these are not included in the
documentation docs, since they return formatted output(boilerplate html & css)

endpoints included here are:
    * CREATE:
    * READ(GET):
        - /users/{user_id}/posts
    * UPDATE:
    * DELETE:
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from webapp.database.config import get_db
from webapp.database import models
from webapp.main import templates

router = APIRouter(prefix="/users")


@router.get("/{user_id}/posts", include_in_schema=False)
def get_user_posts_by_id(
    request: Request, user_id: int, db: Annotated[Session, Depends(get_db)]
):
    """
    returns all posts uploaded by a given user, based on the 'user_id' passed
    in as a parameter. if no posts were uploaded by the given user, appropriate
    error message is returned
    """

    data = db.execute(select(models.User).where(models.User.id == user_id))
    existing_user = data.scalars().first()

    # fail first, fail loudly, keep success clean
    if not existing_user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Looks like the user does not exist. Try again?",
        )

    data = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = data.scalars().all()

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": existing_user,
            "title": f"{existing_user.username.title()}'s Posts",
        },
    )
