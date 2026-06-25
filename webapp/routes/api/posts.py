"""
contain routes for the "/api/posts" endpoints. they return data in JSON format

also these endpoints are what is included in the OpenAPI documentation in:
    - https:127.0.0.1:8000/docs
    - https:127.0.0.1:8000/redoc

endpoints included here are:
    * CREATE(POST):
        - /api/posts: create_post
    * READ(GET):
        - /api/posts: get_posts
        - /api/posts/{post_id}: get_post_by_id
    * UPDATE:
        - PUT: /api/post/{post_id}: update_post_full
        - PATCH: /api/post/{post_id}: update_post_partial
    * DELETE:
        - /api/posts/{post_id}: delete_post_by_id
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from webapp.database import models
from webapp.database.config import get_db
from webapp.schemas.posts import PostCreate, PostResponse, PostUpdate

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    endpoint for creating new posts

    NOTE:
    - 'attribute_names' in the db.commit() refreshes the post alongside the
      table from the relationship passed in, thus ensuring that table values
      and their relationship values are up-to-date
    """
    # verify user first exists
    data = await db.execute(select(models.User).where(models.User.id == post.user_id))
    existing_user = data.scalars().first()

    # fail first, fail visibly, keep success clean
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User of id:{post.user_id} does not exist, try again?",
        )

    new_post = models.Post(title=post.title, content=post.content, user_id=post.user_id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])

    return new_post


@router.get("", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    endpoint that returns all posts in database

    NOTE:
    - "selectinload()": allows for eargely loading in the async sqlite session,
      hence the request is able to access "models.Post.author", lest it would
      return and error
    - "order_by()": arranges them in descending order such that newest posts
      come first.
    """
    data = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
    )
    posts = data.scalars().all()

    return posts


@router.get("/{post_id}")
async def get_post_by_id(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    endpoint returns a specific post by filtering based on it "post_id"

    NOTE:
    - "selectinload()": allows for eargely loading in the async sqlite session,
      hence the request is able to access "models.Post.author", lest it would
      return and error
    """
    data = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id)
    )
    post = data.scalars().first()

    # fail first, fail visibly, keep success clean
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! Looks like the post does not exist. Try again?",
        )

    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(
    post_id: int, updated_post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    endpoint for updating an entire post using PUT.
    all fields are required for this update

    NOTE:
    - "selectinload()": allows for eargely loading in the async sqlite session,
      hence the request is able to access "models.Post.author", lest it would
      return and error
    - "attribute_names" in the db.commit() refreshes the post alongside the
      table from the relationship passed in, thus ensuring that table values
      and their relationship values are up-to-date
    """

    data = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id)
    )
    post = data.scalars().first()

    # ensure post exists
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! Looks like the post does not exist. Try again?",
        )

    # ensure user id matches
    if post.user_id != updated_post.user_id:
        data = await db.execute(
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

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(
    post_id: int, updated_post: PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    endpoint for updating a post partially using PATCH.
    all fields are optional for this update

    NOTE:
    - "selectinload()": allows for eargely loading in the async sqlite session,
      hence the request is able to access "models.Post.author", lest it would
      return and error
    - "attribute_names" in the db.commit() refreshes the post alongside the
      table from the relationship passed in, thus ensuring that table values
      and their relationship values are up-to-date
    """

    data = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id)
    )
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

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_by_id(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    endpoint that deletes a post in the application based on the "post_id"

    does not return anything, but if successful, the response status code is
    204, which means content has successfully been deleted
    """
    data = await db.execute(select(models.Post).where(models.Post.id == post_id))
    existing_post = data.scalars().first()

    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! Post not found, try again?",
        )

    await db.delete(existing_post)
    await db.commit()
