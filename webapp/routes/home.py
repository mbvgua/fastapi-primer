"""
contains routes for the / endpoint. these are not included in the
documentation docs, since they return formatted output(boilerplate html & css)

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
    main aplication endpoint. it redirects to the /posts url, which shows all
    the posts within the application
    """
    return RedirectResponse(url="/posts", status_code=status.HTTP_302_FOUND)
