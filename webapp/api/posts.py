"""
these endpoints return data in JSON format. basic data aimed at giving general
overview of what the application does.

also these endpoints are what is included in the OpenApi documentation in:
    - https:127.0.0.1:8000/docs
    - https:127.0.0.1:8000/redoc

endpoints included here are:
    * CREATE:
        - /api/posts
    * READ(GET):
        - /
        - /posts
        - /posts/{post_id}
    * UPDATE:
    * DELETE:
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
    documentation endopoint for creating posts
    """
    # verify user first exists
    data = db.execute(select(models.User).where(models.User.id == post.user_id))
    existing_user = data.scalars().first()

    # fail first, fail visibly, keep success clean
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User of id:{post.user_id} does not exist, try again?",
        )

    new_post = models.Post(title=post.title, content=post.content, user_id=post.user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    """
    documentation endpoint that returns all posts in application
    """
    data = db.execute(select(models.Post))
    posts = data.scalars().all()

    return posts


@router.get("/{post_id}")
def get_post_by_id(post_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    documentation endpoint that returns a specific post by selecting by its
    post_id
    """
    data = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = data.scalars().first()

    # fail first, fail visibly, keep success clean
    if not post:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Oops! Looks like the post does not exist. Try again?",
        )

    return post
