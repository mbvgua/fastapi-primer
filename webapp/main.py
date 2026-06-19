from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from webapp.database import Base, engine

templates: Jinja2Templates = Jinja2Templates(directory="templates")


def create_app():
    """
    main entrypoint of the application, which uses the factory pattern

    instead of creating an 'app' global variable at the top of the module, it
    is wrapped in a 'create_app()' function, which builds and returns a fresh
    instance when called.
    """

    app = FastAPI()
    # load css & html
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # mount media directory
    app.mount("/media", StaticFiles(directory="media"), name="media")

    # create our database by looking at our models and creating them, if they
    # do not exist. also, this method is idempotent hence safe to run
    # multiple times as it cleans up automatically
    from webapp import models

    Base.metadata.create_all(bind=engine)

    # import & register the routes
    from webapp.routes.home import router as home_router
    from webapp.routes.posts import router as posts_router
    from webapp.routes.users import router as users_router
    from webapp.api.users import router as users_api_router
    from webapp.api.posts import router as posts_api_router

    app.include_router(home_router)
    app.include_router(users_router)
    app.include_router(posts_router)
    app.include_router(users_api_router)
    app.include_router(posts_api_router)

    # error handling
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    @app.exception_handler(StarletteHTTPException)
    def general_http_exception_handler(
        request: Request, exception: StarletteHTTPException
    ):
        """
        handle exception handlers. this catches any StarletteHTTPException's
        raised via code execution.

        fastapi is built on top of starlette, hence why its execptions are also imported
        alongside those of fastapi, lest some will be missed.
        """
        message = (
            exception.detail if exception.detail else "An error occurred, try again?"
        )

        # if url starts with "/api/..." return JSON response
        if request.url.path.startswith("/api"):
            return JSONResponse(
                status_code=exception.status_code, content={"detail": message}
            )
        # else return 'error.html' template
        else:
            return templates.TemplateResponse(
                request,
                "error.html",
                {
                    "status_code": exception.status_code,
                    "title": exception.status_code,
                    "message": message,
                },
                status_code=exception.status_code,
            )

    # Validation Error Handling
    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(
        request: Request, exception: RequestValidationError
    ):
        """
        handle validation errors
        """
        message = "An error occurred, try again?"

        # if url starts with "/api/..." return JSON response
        if request.url.path.startswith("/api"):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                content={"detail": exception.errors()},
            )
        # else return 'error.html' template
        else:
            return templates.TemplateResponse(
                request,
                "error.html",
                {
                    "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
                    "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
                    "message": message,
                },
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            )

    return app


# yes, I floss
message = """
Copyright (C) 2026 <@mbvgua>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
