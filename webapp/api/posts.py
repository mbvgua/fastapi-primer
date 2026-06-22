"""
these endpoints return data in JSON format. basic data aimed at giving general
overview of what the application does.

also these endpoints are what is included in the OpenApi documentation in:
    - https:127.0.0.1:8000/docs
    - https:127.0.0.1:8000/redoc

endpoints included here are:
    * CREATE(POST):
        - /api/posts
    * READ(GET):
        - /api/posts
        - /api/posts/{post_id}
    * UPDATE:
        - PUT: /api/post/{post_id}
        - PATCH: /api/post/{post_id}
    * DELETE:
        - /api/posts/{post_id}
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from webapp.database import models
from webapp.database.config import get_db
from webapp.schemas.posts import PostCreate, PostResponse, PostUpdate

router = APIRouter(prefix="/api/posts")


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! Looks like the post does not exist. Try again?",
        )

    return post


@router.put("/{post_id}", response_model=PostResponse)
def update_post_full(
    post_id: int, updated_post: PostCreate, db: Annotated[Session, Depends(get_db)]
):
    """
    documentation endpoint for updating an entire post using *PUT*
    all fields are required for this update
    """

    data = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = data.scalars().first()

    # ensure post exists
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! Looks like the post does not exist. Try again?",
        )

    # ensure user id matches
    if post.user_id != updated_post.user_id:
        data = db.execute(
            select(models.User).where(models.User.id == updated_post.user_id)
        )
        existing_user = data.scalars().first()

        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Oops! looks like the user does not exist. Try again?",
            )

    post.title = updated_post.title
    post.content = updated_post.content
    post.user_id = updated_post.user_id

    db.commit()
    db.refresh(post)
    return post


@router.patch("/{post_id}", response_model=PostResponse)
def update_post_partial(
    post_id: int, updated_post: PostUpdate, db: Annotated[Session, Depends(get_db)]
):
    """
    documentation endpoint for updating a post partially using *PATCH*
    all fields are optional for this update
    """

    data = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = data.scalars().first()

    # ensure post exists
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! Looks like the post does not exist. Try again?",
        )

    # overwrites only the data fields passed in by the user, and not update all
    # of them, as those maybe become what is set as default ->'None'
    updated_data = updated_post.model_dump(exclude_unset=True)

    # .model_dump returns a dictionary
    for field, value in updated_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_by_id(post_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    documentation endpoint that deletes a post in the application based on the
    'post_id' passed in

    does not return anything, but if successful, the response status code is
    204, which means content has successfully been deleted
    """
    data = db.execute(select(models.Post).where(models.Post.id == post_id))
    existing_post = data.scalars().first()

    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! Post not found, try again?",
        )

    db.delete(existing_post)
    db.commit()
