"""
contains routes for the "/auth" endpoints.

these routes will not be included in the documentation docs, since they
return formatted output in html & css.

endpoints included here are:
    * CREATE:
    * READ(GET):
        - /login: login
        - /register: register
    * UPDATE:
    * DELETE:
"""
from fastapi import APIRouter, Request

from webapp.main import templates

router = APIRouter(prefix="/auth", include_in_schema=False)


@router.get("/register")
async def register(request: Request):
    """
    "/auth/register"
    endpoint that registers new users into the application.

    most of the logic performed is contained inline in the
    "templates/register.html" template, which it renders, formatted in html and
    css. the template calls the "/api/users" endpoint, using javascript, to
    create a new user in the database if all input values are correct. if not
    appropriate errors are returned.

    the user is then redirect to the "/auth/login" route to get their token
    assigned before being logged into the application.
    """
    title: str = "Register"
    return templates.TemplateResponse(request, "register.html", {"title": title})


@router.get("/login")
async def login(request: Request):
    """
    "/auth/login"
    endpoint that logs in existing users into the application.

    most of the logic performed is contained inline in the
    "templates/login.html" template, which it renders, formatted in html and
    css.

    the template calls the "/api/auth/token" endpoint, using javascript,
    which peforms most of the logic, checking if the user exists in the
    database, then assigning them their token and logging them in.
    """
    title: str = "Login"
    return templates.TemplateResponse(request, "login.html", {"title": title})
