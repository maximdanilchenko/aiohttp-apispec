# views.py
from aiohttp import web

from aiohttp_apispec import docs, request_schema

from .schemas import Message, User, UsersList


@docs(
    tags=["users"],
    summary="Get users list",
    description="Get list of all users from our toy database",
    responses={
        200: {"description": "Ok. Users list", "schema": UsersList},
        404: {"description": "Not Found"},
        500: {"description": "Server error"},
    },
)
async def get_users(request: web.Request):
    return web.json_response({"users": request.app["users"]})


@docs(
    tags=["users"],
    summary="Create new user",
    description="Add new user to our toy database",
    responses={
        200: {"description": "Ok. User created", "schema": Message},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
        500: {"description": "Server error"},
    },
)
@request_schema(User, location='query')
async def create_user(request: web.Request):
    new_user = request["data"]
    request.app["users"].append(new_user)
    return web.json_response({"message": f"Hello {new_user['name']}!"})
