# routes.py
from aiohttp import web

from .views import get_users, create_user


def setup_routes(app: web.Application):
    app.router.add_get("/users", get_users)
    app.router.add_post("/users", create_user)
