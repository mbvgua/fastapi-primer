from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)

from webapp.database.config import Base, engine

templates: Jinja2Templates = Jinja2Templates(directory="templates")


def create_app():
    """
    main entrypoint of the application, which uses the factory pattern

    instead of creating an 'app' global variable at the top of the module, it
    is wrapped in a 'create_app()' function, which builds and returns a fresh
    instance when called.
    """

    # create our database by looking at our models and creating them, if they
    # do not exist. also, this method is idempotent hence safe to run
    # multiple times as it cleans up automatically
    from webapp.database import models

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        lifespan are modern methods in FastAPI to handle the startup and
        shutdown of events. they replace deprecated 'on_startup'/'on_shutdown'
        that were common in Flask applications.

        previously, the db was created with:
            $ Base.metadata.create_all(bind=engine)

        'create_all' was synchronous, hence unable to be called alongside
        asynchronous methods. lifespans allow for this
        """
        # startup
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield

        # shutdown
        await engine.dispose()

    app = FastAPI(
        title="fastapi-primer",
        description="simple app for recording user posts",
        version="0.0.1",
        lifespan=lifespan,
        license_info={
            "name": "GPLv3",
            "url": "https://www.gnu.org/licenses/gpl-3.0.en.html",
        },
        # enable this once the project goes live, to disable the api docs
        # openapi_url=None,
    )

    # load css & html
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # mount media directory
    app.mount("/media", StaticFiles(directory="media"), name="media")

    # import & register the routes
    from webapp.routes.home import router as home_router
    from webapp.routes.posts import router as posts_router
    from webapp.routes.users import router as users_router
    from webapp.routes.api.users import router as users_api_router
    from webapp.routes.api.posts import router as posts_api_router

    app.include_router(home_router)
    app.include_router(users_router)
    app.include_router(posts_router)
    app.include_router(users_api_router)
    app.include_router(posts_api_router)

    # error handling
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    @app.exception_handler(StarletteHTTPException)
    async def general_http_exception_handler(
        request: Request, exception: StarletteHTTPException
    ):
        """
        handle exception errors asynchronously.
        this catches any StarletteHTTPException's raised via code execution.

        fastapi is built on top of starlette, hence why its execptions are also imported
        alongside those of fastapi, lest some will be missed.
        """
        # if url starts with "/api/..."
        if request.url.path.startswith("/api"):
            return await http_exception_handler(request, exception)

        message = (
            exception.detail
            if exception.detail
            else "An error occurred. Please check your request and try again?"
        )

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
    async def validation_exception_handler(
        request: Request, exception: RequestValidationError
    ):
        """
        handle validation errors asynchronously
        """

        # if url starts with "/api/..." return JSON response
        if request.url.path.startswith("/api"):
            return await request_validation_exception_handler(request, exception)

        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
                "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
                "message": "Invalid request, please check your input and try again.",
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
