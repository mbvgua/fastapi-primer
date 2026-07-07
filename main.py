"""
basic fastAPI server. To run the program:
    $ fastapi dev main.py

once the server has been started, api documentation can be found at:
    - https:127.0.0.1:8000/docs
    - https:127.0.0.1:8000/redoc
"""

from webapp.main import create_app

app = create_app()
