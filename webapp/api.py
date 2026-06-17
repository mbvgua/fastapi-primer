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

from fastapi import APIRouter
from starlette.status import HTTP_201_CREATED

from . import posts
from .validators import PostCreate, PostResponse

router = APIRouter()


@router.post("/api/posts/", response_model=PostResponse, status_code=HTTP_201_CREATED)
def create_post(post: PostCreate):
    """
    endpoint for creating posts in JSON format
    """
    # create new post id, appending by 1 to the existing, else makeit 1
    new_id = max(post["id"] for post in posts) + 1 if posts else 1

    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "January 01,2025",
    }
    posts.append(new_post)
    return new_post


@router.get("/api/posts/", response_model=list[PostResponse])
def get_posts_api():
    """
    API endpoint to return all posts within the application in JSON format
    """
    return posts


@router.get("/api/posts/{post_id}")
def get_post_api(post_id: int, response_model=PostResponse):
    """
    return specific post by narrowing down with its ID
    """
    error_message = "Oops! Looks like the post does not exist. Try again?"
    for post in posts:
        if post.get("id") == post_id:
            return post

    return {"error": error_message}
