"""
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

* main.py - basic fastAPI server. To run the program:
    $ fastapi dev main.py

  once the server has been started, api documentation can be found at:
    - https:127.0.0.1:8000/docs
    - https:127.0.0.1:8000/redoc
"""

from webapp.main import create_app

app = create_app()
