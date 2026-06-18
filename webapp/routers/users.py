from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from webapp.database import get_db
from webapp import models
from webapp.main import templates

router = APIRouter(prefix="/users")


@router.get("/{user_id}/posts", include_in_schema=False)
def get_user_posts(
    request: Request, user_id: int, db: Annotated[Session, Depends(get_db)]
):
    """
    endpoint returns all posts uploaded by a given user
    """
    result = db.execute(select(models.User).where(models.User.id == user_id))
    existing_user = result.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Oh no! Looks like the user does not exist, try again?",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": existing_user,
            "title": f"{existing_user.username.title()}'s Posts",
        },
    )
