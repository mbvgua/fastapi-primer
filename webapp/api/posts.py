"""
these endpoints return data in JSON format. basic data aimed at giving general
overview of what the application does. also these endpoints are what is
included in the OpenApi documentation in:
    - https:127.0.0.1:8000/docs
    - https:127.0.0.1:8000/redoc

URL's include:
    * POST:
        - /api/posts
    * GET:
        - /api/posts
        - /api/posts/{post_id}
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from webapp import models
from webapp.database import get_db
from webapp.schemas.posts import PostCreate, PostResponse

router = APIRouter(prefix="/api/posts")


@router.post("/", response_model=PostResponse, status_code=HTTP_201_CREATED)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    """
    endpoint for creating posts in JSON format
    """
    # verify user first exists
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    existing_user = result.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist, try again?",
        )

    new_post = models.Post(title=post.title, content=post.content, user_id=post.user_id)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/", response_model=list[PostResponse])
def get_posts_api(db: Annotated[Session, Depends(get_db)]):
    """
    API endpoint to return all posts within the application in JSON format
    """
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts


@router.get("/{post_id}")
def get_post_api(post_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    return specific post by narrowing down with its ID
    """
    error_message = "Oops! Looks like the post does not exist. Try again?"
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=error_message)

    return post
