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
- [x] file uploads: image processing , validation & storage
- [x] pagination
- [x] password resets & background processes
- [x] database migrations with alembic & ~~PostgreSql~~ MariaDb
- [ ] moving files to the cloud with AWS S3 & Boto
- [ ] testing with pytest
- [ ] deployment with nginx & custom domains
- [ ] deployment with docker & serverless containers

## detours

- [x] thorough modularization of the application earlier on. Was accustomed to the good old factory settings from flask, hence applied that methodology here.
- [x] implement code reusability by defining a "utils" directory, where I placed small Classes & functions for reuse.
- [ ] do tokens expire even when a user is active? figure out to to see if user is active in the frontend and prolong token expiration
- [ ] implement oauth with google
- [ ] add protected admin only routes for admins only
- [ ] add an admin panel
- [x] used Resend instead of MailTrap
- [ ] when user is logged in and they change their password, all prior sessions must be terminated. for security
- [ ] use a taskque for emails, although not critical. e.g Celery, Rabitt Mq
- [ ] use MariaDB+aiomysql instead of Postgres+pscoppg. [why?](./populate_images/2026-08-27_11-19.png)
