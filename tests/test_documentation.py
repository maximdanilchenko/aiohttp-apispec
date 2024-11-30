from aiohttp import web
from aiohttp.web_urldispatcher import StaticResource
from yarl import URL

from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_apispec.aiohttp_apispec import OpenApiVersion


def ref_resolver(openapi_version, ref):
    if openapi_version == OpenApiVersion.V20:
        return f"#/definitions/{ref}"
    return f"#/components/schemas/{ref}"


def parameter_description(openapi_version, source, **kwargs):
    if openapi_version == OpenApiVersion.V20:
        source.update(**kwargs)
    else:
        source["schema"] = kwargs
    return source


def parameter_list_description(openapi_version, source, **kwargs):
    if openapi_version == OpenApiVersion.V20:
        source.update(**kwargs)
        source["collectionFormat"] = "multi"
    else:
        source["schema"] = kwargs
        source["explode"] = True
        source["style"] = "form"
    return source


def request_schema_description(openapi_version, source, ref):
    if openapi_version == OpenApiVersion.V20:
        schema = {"$ref": ref_resolver(openapi_version, ref)}
    else:
        schema = {"schema": {"$ref": ref_resolver(openapi_version, ref)}}
    source.update(schema)
    return source


def response_schema_description(openapi_version, source, ref):
    print(source)
    if openapi_version == OpenApiVersion.V20:
        schema = {"schema": {"$ref": ref_resolver(openapi_version, ref)}}
    else:
        schema = {
            "content": {
                "application/json": {
                    "schema": {"$ref": ref_resolver(openapi_version, ref)}
                }
            }
        }
    source.update(schema)
    return source


def test_app_swagger_url(aiohttp_app):
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


async def test_app_swagger_json(aiohttp_app, example_for_request_schema):
    resp = await aiohttp_app.get("/v1/api/docs/api-docs")
    docs = await resp.json()
    assert docs["info"]["title"] == "API documentation"
    assert docs["info"]["version"] == "0.0.1"
    openapi_version = OpenApiVersion(docs.get("openapi", "2.0"))

    docs["paths"]["/v1/test"]["get"]["parameters"] = sorted(
        docs["paths"]["/v1/test"]["get"]["parameters"], key=lambda x: x["name"]
    )
    assert docs["paths"]["/v1/test"]["get"] == {
        "parameters": [
            parameter_description(
                openapi_version,
                {
                    "in": "query",
                    "name": "bool_field",
                    "required": False,
                },
                type="boolean",
            ),
            parameter_description(
                openapi_version,
                {
                    "in": "query",
                    "name": "id",
                    "required": False,
                },
                type="integer",
            ),
            parameter_list_description(
                openapi_version,
                {
                    "in": "query",
                    "name": "list_field",
                    "required": False,
                },
                type="array",
                items={"type": "integer"},
            ),
            parameter_description(
                openapi_version,
                {
                    "description": "name",
                    "in": "query",
                    "name": "name",
                    "required": False,
                },
                type="string",
            ),
            request_schema_description(
                openapi_version,
                {
                    # default schema_name_resolver, resolved based on schema __name__
                    # drops trailing "Schema so, MyNestedSchema resolves to MyNested
                    "in": "query",
                    "name": "nested_field",
                    "required": False,
                },
                "MyNested",
            ),
        ],
        "responses": {
            "200": response_schema_description(
                openapi_version,
                {
                    "description": "Success response",
                },
                "Response",
            ),
            "404": {"description": "Not Found"},
        },
        "tags": ["mytag"],
        "summary": "Test method summary",
        "description": "Test method description",
        "produces": ["application/json"],
    }
    docs["paths"]["/v1/class_echo"]["get"]["parameters"] = sorted(
        docs["paths"]["/v1/class_echo"]["get"]["parameters"], key=lambda x: x["name"]
    )
    assert docs["paths"]["/v1/class_echo"]["get"] == {
        "parameters": [
            parameter_description(
                openapi_version,
                {
                    "in": "query",
                    "name": "bool_field",
                    "required": False,
                },
                type="boolean",
            ),
            parameter_description(
                openapi_version,
                {
                    "in": "query",
                    "name": "id",
                    "required": False,
                },
                type="integer",
            ),
            parameter_list_description(
                openapi_version,
                {
                    "in": "query",
                    "name": "list_field",
                    "required": False,
                },
                type="array",
                items={"type": "integer"},
            ),
            parameter_description(
                openapi_version,
                {
                    "description": "name",
                    "in": "query",
                    "name": "name",
                    "required": False,
                },
                type="string",
            ),
            request_schema_description(
                openapi_version,
                {
                    "in": "query",
                    "name": "nested_field",
                    "required": False,
                },
                "MyNested",
            ),
        ],
        "responses": {},
        "tags": ["mytag"],
        "summary": "View method summary",
        "description": "View method description",
        "produces": ["application/json"],
    }

    if openapi_version == OpenApiVersion.V20:
        assert docs["paths"]["/v1/example_endpoint"]["post"]["parameters"] == [
            {
                'in': 'body',
                'required': False,
                'name': 'body',
                'schema': {
                    'allOf': [
                        {
                            '$ref': f'#/definitions/{ref_resolver(openapi_version, "Request")}'
                        }
                    ],
                    'example': example_for_request_schema,
                },
            }
        ]
    else:
        assert docs["paths"]["/v1/example_endpoint"]["post"]["requestBody"] == {
            "content": {
                "application/json": {
                    'required': False,
                    'schema': {
                        'allOf': [
                            {
                                '$ref': f'#/components/schemas/{ref_resolver(openapi_version, "Request")}'
                            }
                        ],
                        'example': example_for_request_schema,
                    },
                }
            }
        }

    _request_properties = {
        "properties": {
            "bool_field": {"type": "boolean"},
            "id": {"type": "integer"},
            "list_field": {
                "items": {"type": "integer"},
                "type": "array",
            },
            "name": {"description": "name", "type": "string"},
            "nested_field": {"$ref": ref_resolver(openapi_version, "MyNested")},
        },
        "type": "object",
    }

    if openapi_version == OpenApiVersion.V20:
        assert docs["definitions"] == {
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
        }
    else:
        assert docs["components"]["schemas"] == {
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
        }


async def test_not_register_route_for_none_url():
    app = web.Application()
    routes_count = len(app.router.routes())
    setup_aiohttp_apispec(app=app, url=None)
    routes_count_after_setup_apispec = len(app.router.routes())
    assert routes_count == routes_count_after_setup_apispec


async def test_register_route_for_relative_url():
    app = web.Application()
    routes_count = len(app.router.routes())
    assert routes_count == 0
    setup_aiohttp_apispec(app=app, url="api/swagger")
    # new route should be registered according to AiohttpApispec.register() method?
    routes_count_after_setup_apispec = len(app.router.routes())
    # not sure why there was a comparison between the old rount_count vs new_route_count
    assert routes_count_after_setup_apispec == 1
