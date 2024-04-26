from typing import Any, Dict

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient
from marshmallow import EXCLUDE, INCLUDE, Schema, fields

from aiohttp_apispec import (
    cookies_schema,
    docs,
    headers_schema,
    json_schema,
    match_info_schema,
    querystring_schema,
    request_schema,
    response_schema,
    setup_aiohttp_apispec,
    validation_middleware,
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


class HeaderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    some_header = fields.String()


class MatchInfoSchema(Schema):
    uuid = fields.Integer()


class CookiesSchema(Schema):
    some_cookie = fields.String()


def pytest_report_header(config):
    return """
          .   .  .                                   
,-. . ,-. |-. |- |- ,-.    ,-. ,-. . ,-. ,-. ,-. ,-. 
,-| | | | | | |  |  | | -- ,-| | | | `-. | | |-' |   
`-^ ' `-' ' ' `' `' |-'    `-^ |-' ' `-' |-' `-' `-' 
                    |          |         |           
                    '          '         '           
    """


class MyNestedSchema(Schema):
    i = fields.Int()


class RequestSchema(Schema):
    id = fields.Int()
    name = fields.Str(metadata={"description": "name"})
    bool_field = fields.Bool()
    list_field = fields.List(fields.Int())
    nested_field = fields.Nested(MyNestedSchema)


class ResponseSchema(Schema):
    msg = fields.Str()
    data = fields.Dict()


class MyException(Exception):
    def __init__(self, message):
        self.message = message


@pytest.fixture
def example_for_request_schema() -> Dict[str, Any]:
    return {
        'id': 1,
        'name': 'test',
        'bool_field': True,
        'list_field': [1, 2, 3],
        'nested_field': {'i': 12},
    }


@pytest.fixture(
    # since multiple locations are no longer supported
    # in a single call, location should always expect string
    params=[
        ({"location": "querystring"}, True),
        ({"location": "querystring"}, True),
        ({"location": "querystring"}, False),
        ({"location": "querystring"}, False),
    ]
)
async def aiohttp_app(
    aiohttp_client: TestClient,
    request: pytest.FixtureRequest,
    example_for_request_schema: Dict[str, Any],
):
    location, nested = request.param

    @docs(
        tags=["mytag"],
        summary="Test method summary",
        description="Test method description",
        responses={404: {"description": "Not Found"}},
    )
    @request_schema(RequestSchema, **location)
    @response_schema(ResponseSchema, 200, description="Success response")
    async def handler_get(request):
        return web.json_response({"msg": "done", "data": {}})

    @request_schema(RequestSchema)
    async def handler_post(request):
        return web.json_response({"msg": "done", "data": {}})

    @request_schema(RequestSchema, example=example_for_request_schema)
    async def handler_post_with_example_to_endpoint(request):
        return web.json_response({"msg": "done", "data": {}})

    @request_schema(RequestSchema, example=example_for_request_schema, add_to_refs=True)
    async def handler_post_with_example_to_ref(request):
        return web.json_response({"msg": "done", "data": {}})

    @request_schema(RequestSchema(partial=True))
    async def handler_post_partial(request):
        return web.json_response({"msg": "done", "data": {}})

    @request_schema(RequestSchema())
    async def handler_post_callable_schema(request):
        return web.json_response({"msg": "done", "data": {}})

    @request_schema(RequestSchema)
    async def handler_post_echo(request):
        return web.json_response(request["data"])

    @request_schema(RequestSchema, **location)
    async def handler_get_echo(request):
        return web.json_response(request["data"])

    @docs(
        parameters=[
            {
                "in": "path",
                "name": "var",
                "schema": {"type": "string", "format": "uuid"},
            }
        ]
    )
    async def handler_get_variable(request):
        return web.json_response(request["data"])

    class ViewClass(web.View):
        @docs(
            tags=["mytag"],
            summary="View method summary",
            description="View method description",
        )
        @request_schema(RequestSchema, **location)
        async def get(self):
            return web.json_response(self.request["data"])

        async def delete(self):
            return web.json_response({"hello": "world"})

    async def other(request):
        return web.Response()

    def my_error_handler(error, req, schema, *args, error_status_code, error_headers):
        raise MyException({"errors": error.messages, "text": "Oops"})

    @web.middleware
    async def intercept_error(request, handler):
        try:
            return await handler(request)
        except MyException as e:
            return web.json_response(e.message, status=400)

    @match_info_schema(MatchInfoSchema)
    @querystring_schema(RequestSchema)
    @json_schema(RequestSchema)
    @headers_schema(HeaderSchema)
    @cookies_schema(CookiesSchema)
    async def validated_view(request: web.Request):
        return web.json_response(
            {
                "json": request["json"],
                "headers": request["headers"],
                "cookies": request["cookies"],
                "match_info": request["match_info"],
                "querystring": request["querystring"],
            }
        )

    app = web.Application()
    if nested:
        v1 = web.Application()
        setup_aiohttp_apispec(
            app=v1,
            title="API documentation",
            version="0.0.1",
            url="/api/docs/api-docs",
            swagger_path="/api/docs",
            error_callback=my_error_handler,
        )
        v1.router.add_routes(
            [
                web.get("/test", handler_get),
                web.post("/test", handler_post),
                web.post("/example_endpoint", handler_post_with_example_to_endpoint),
                web.post("/example_ref", handler_post_with_example_to_ref),
                web.post("/test_partial", handler_post_partial),
                web.post("/test_call", handler_post_callable_schema),
                web.get("/other", other),
                web.get("/echo", handler_get_echo),
                web.view("/class_echo", ViewClass),
                web.post("/echo", handler_post_echo),
                web.get("/variable/{var}", handler_get_variable),
                web.post("/validate/{uuid}", validated_view),
            ]
        )
        v1.middlewares.extend([intercept_error, validation_middleware])
        app.add_subapp("/v1/", v1)
    else:
        setup_aiohttp_apispec(
            app=app,
            url="/v1/api/docs/api-docs",
            swagger_path="/v1/api/docs",
            error_callback=my_error_handler,
        )
        app.router.add_routes(
            [
                web.get("/v1/test", handler_get),
                web.post("/v1/test", handler_post),
                web.post("/v1/example_endpoint", handler_post_with_example_to_endpoint),
                web.post("/v1/example_ref", handler_post_with_example_to_ref),
                web.post("/v1/test_partial", handler_post_partial),
                web.post("/v1/test_call", handler_post_callable_schema),
                web.get("/v1/other", other),
                web.get("/v1/echo", handler_get_echo),
                web.view("/v1/class_echo", ViewClass),
                web.post("/v1/echo", handler_post_echo),
                web.get("/v1/variable/{var}", handler_get_variable),
                web.post("/v1/validate/{uuid}", validated_view),
            ]
        )
        app.middlewares.extend([intercept_error, validation_middleware])

    client = await aiohttp_client(app)
    return client
