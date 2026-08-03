# Learning FastAPI

In this repo I intend to dive into the intricacies of FastApi framework, while following along
to [Corey Schafer's](https://youtube.com/playlist?list=PL-osiE80TeTsak-c-QsVeg0YYG_0TeyXI&si=TcfJfQRVEnpWkbqN) guide.

Core technologies learnt:

- [x] using jinja2 templates
- [x] styling with bootstrap
- [x] validation and error handling
- [x] pydantic schemas & models for data validation
- [x] using SQLAlchemy ORM
- [x] performing CRUD(Create, Read, Update, Delete) operations
- [x] making your app asynchronous
- [x] routers with APIRouter
- [x] forms
- [x] authentication: registration & login
- [x] authorization: protecting routes
- [ ] file uploads: image processing , validation & storage
- [ ] pagination
- [ ] password resets & background processes
- [ ] database migrations with alembic & PostgreSql
- [ ] moving files to the cloud with AWS S3 & Boto
- [ ] testing with pytest
- [ ] deployment with nginx & custom domains
- [ ] deployment with docker & serverless containers

## Detours

- thorough modularization of the application earlier on. Was accustomed to the good old factory settings from flask, hence applied that methodology here.
- implement code reusability by defining a "utils" directory, where I placed small Classes & functions for reuse.
- implement oauth with google
