import json

import pytest
from aiohttp import web
from aiohttp.web_urldispatcher import StaticResource
from yarl import URL

from aiohttp_apispec import setup_aiohttp_apispec


@pytest.mark.anyio
async def test_app_swagger_url(aiohttp_app):
    def safe_url_for(route):
        if isinstance(route._resource, StaticResource):
            # url_for on StaticResource requires filename arg
            return None
        try:
            return route.url_for()
        except KeyError:
            return None

    urls = [safe_url_for(route) for route in aiohttp_app.app.router.routes()]
    assert URL("/v1/api/docs/api-docs") in urls


@pytest.mark.anyio
async def test_app_swagger_json(aiohttp_app, example_for_request_schema):
    resp = await aiohttp_app.get("/v1/api/docs/api-docs")
    docs = await resp.json()
    assert docs["info"]["title"] == "API documentation"
    assert docs["info"]["version"] == "0.0.1"
    docs["paths"]["/v1/test"]["get"]["parameters"] = sorted(
        docs["paths"]["/v1/test"]["get"]["parameters"], key=lambda x: x["name"]
    )
    assert json.dumps(docs["paths"]["/v1/test"]["get"], sort_keys=True) == json.dumps(
        {
            "parameters": [
                {
                    "in": "query",
                    "name": "bool_field",
                    "required": False,
                    "type": "boolean",
                },
                {
                    "in": "query",
                    "name": "id",
                    "required": False,
                    "type": "integer",
                },
                {
                    "collectionFormat": "multi",
                    "in": "query",
                    "items": {"type": "integer"},
                    "name": "list_field",
                    "required": False,
                    "type": "array",
                },
                {
                    "description": "name",
                    "in": "query",
                    "name": "name",
                    "required": False,
                    "type": "string",
                },
                {
                    # default schema_name_resolver, resolved based on schema __name__
                    # drops trailing "Schema so, MyNestedSchema resolves to MyNested
                    "$ref": "#/definitions/MyNested",
                    "in": "query",
                    "name": "nested_field",
                    "required": False,
                },
            ],
            "responses": {
                "200": {
                    "description": "Success response",
                    "schema": {"$ref": "#/definitions/Response"},
                },
                "404": {"description": "Not Found"},
            },
            "tags": ["mytag"],
            "summary": "Test method summary",
            "description": "Test method description",
            "produces": ["application/json"],
        },
        sort_keys=True,
    )
    docs["paths"]["/v1/class_echo"]["get"]["parameters"] = sorted(
        docs["paths"]["/v1/class_echo"]["get"]["parameters"], key=lambda x: x["name"]
    )
    assert json.dumps(
        docs["paths"]["/v1/class_echo"]["get"], sort_keys=True
    ) == json.dumps(
        {
            "parameters": [
                {
                    "in": "query",
                    "name": "bool_field",
                    "required": False,
                    "type": "boolean",
                },
                {
                    "in": "query",
                    "name": "id",
                    "required": False,
                    "type": "integer",
                },
                {
                    "collectionFormat": "multi",
                    "in": "query",
                    "items": {"type": "integer"},
                    "name": "list_field",
                    "required": False,
                    "type": "array",
                },
                {
                    "description": "name",
                    "in": "query",
                    "name": "name",
                    "required": False,
                    "type": "string",
                },
                {
                    "$ref": "#/definitions/MyNested",
                    "in": "query",
                    "name": "nested_field",
                    "required": False,
                },
            ],
            "responses": {},
            "tags": ["mytag"],
            "summary": "View method summary",
            "description": "View method description",
            "produces": ["application/json"],
        },
        sort_keys=True,
    )
    assert docs["paths"]["/v1/example_endpoint"]["post"]["parameters"] == [
        {
            'in': 'body',
            'required': False,
            'name': 'body',
            'schema': {
                'allOf': [{'$ref': '#/definitions/#/definitions/Request'}],
                'example': example_for_request_schema,
            },
        }
    ]

    _request_properties = {
        "properties": {
            "bool_field": {"type": "boolean"},
            "id": {"type": "integer"},
            "list_field": {
                "items": {"type": "integer"},
                "type": "array",
            },
            "name": {"description": "name", "type": "string"},
            "nested_field": {"$ref": "#/definitions/MyNested"},
        },
        "type": "object",
    }
    assert json.dumps(docs["definitions"], sort_keys=True) == json.dumps(
        {
            "MyNested": {
                "properties": {"i": {"type": "integer"}},
                "type": "object",
            },
            "Request": {**_request_properties, 'example': example_for_request_schema},
            "Partial-Request": _request_properties,
            "Response": {
                "properties": {"data": {"type": "object"}, "msg": {"type": "string"}},
                "type": "object",
            },
        },
        sort_keys=True,
    )


@pytest.mark.anyio
async def test_not_register_route_for_none_url():
    app = web.Application()
    routes_count = len(app.router.routes())
    setup_aiohttp_apispec(app=app, url=None)
    routes_count_after_setup_apispec = len(app.router.routes())
    assert routes_count == routes_count_after_setup_apispec


@pytest.mark.anyio
async def test_register_route_for_relative_url():
    app = web.Application()
    routes_count = len(app.router.routes())
    assert routes_count == 0
    setup_aiohttp_apispec(app=app, url="api/swagger")
    # new route should be registered according to AiohttpApispec.register() method?
    routes_count_after_setup_apispec = len(app.router.routes())
    # not sure why there was a comparison between the old rount_count vs new_route_count
    assert routes_count_after_setup_apispec == 1
