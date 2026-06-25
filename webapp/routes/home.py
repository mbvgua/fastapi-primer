"""
contains routes for the "/" endpoint.

these routes will not be included in the documentation docs, as since they
return formatted output in html & css.

endpoints included here are:
    * CREATE:
    * READ(GET):
        - /
    * UPDATE:
    * DELETE:
"""

from fastapi import status, APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/", name="home", include_in_schema=False)
def home():
    """
    this is the main application endpoint.

    it redirects to the "/posts" url, which shows all the posts
    in the application
    """

    return RedirectResponse(url="/posts", status_code=status.HTTP_302_FOUND)
