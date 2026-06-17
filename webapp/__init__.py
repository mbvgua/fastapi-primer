from pathlib import Path

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

# posts json db
posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]
templates: Jinja2Templates = Jinja2Templates(directory="templates")


def create_app():
    app = FastAPI()
    # load css & html
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # include routes
    from .routes import router as routes_router
    app.include_router(routes_router)

    from .api import router as api_router
    app.include_router(api_router)

    # error handling
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    # Exception Handling
    @app.exception_handler(StarletteHTTPException)
    def general_http_exception_handler(
        request: Request, exception: StarletteHTTPException
    ):
        """
        use exception handler to catch any StarletteHTTPException's raised via code
        execution.

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
        hanlde validation errors
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
