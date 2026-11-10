# TODOs

- [x] thorough modularization of the application earlier on. Was accustomed to the good old factory settings from flask, hence applied that methodology here.
- [x] implement code reusability by defining a "utils" directory, where I placed small Classes & functions for reuse.
- [ ] do tokens expire even when a user is active? figure out to to see if user is active in the frontend and prolong token expiration
- [ ] implement oauth with google
- [ ] add protected admin only routes for admins only
- [ ] add an admin panel
- [ ] when user is logged in and they change their password, all prior sessions must be terminated. for security
- [ ] use a task queue for emails, although not critical. e.g Celery, Rabitt Mq
