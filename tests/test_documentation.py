import json
from yarl import URL


OPENAPI_20_V1_TEST_SCHEMA = {
    "parameters": [
        {"in": "query", "name": "bool_field", "required": False, "type": "boolean"},
        {
            "format": "int32",
            "in": "query",
            "name": "id",
            "required": False,
            "type": "integer",
        },
        {
            "collectionFormat": "multi",
            "in": "query",
            "items": {"format": "int32", "type": "integer"},
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
}

OPENAPI_20_V1_CLASS_ECHO_SCHEMA = {
    "parameters": [
        {"in": "query", "name": "bool_field", "required": False, "type": "boolean"},
        {
            "format": "int32",
            "in": "query",
            "name": "id",
            "required": False,
            "type": "integer",
        },
        {
            "collectionFormat": "multi",
            "in": "query",
            "items": {"format": "int32", "type": "integer"},
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
    ],
    "responses": {},
    "tags": ["mytag"],
    "summary": "View method summary",
    "description": "View method description",
    "produces": ["application/json"],
}

OPENAPI_20_DEFINITIONS_SCHEMA = {
    "Response": {
        "type": "object",
        "properties": {"msg": {"type": "string"}, "data": {"type": "object"}},
    },
    "Request": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "name"},
            "bool_field": {"type": "boolean"},
            "list_field": {
                "type": "array",
                "items": {"type": "integer", "format": "int32"},
            },
            "id": {"type": "integer", "format": "int32"},
        },
    },
    "Request1": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "name"},
            "bool_field": {"type": "boolean"},
            "list_field": {
                "type": "array",
                "items": {"type": "integer", "format": "int32"},
            },
            "id": {"type": "integer", "format": "int32"},
        },
    },
}

SCHEMAS_MAPPING = {
    "2.0": (
        OPENAPI_20_V1_TEST_SCHEMA,
        OPENAPI_20_V1_CLASS_ECHO_SCHEMA,
        OPENAPI_20_DEFINITIONS_SCHEMA,
    ),
    "2.1": (
        OPENAPI_20_V1_TEST_SCHEMA,
        OPENAPI_20_V1_CLASS_ECHO_SCHEMA,
        OPENAPI_20_DEFINITIONS_SCHEMA,
    ),
}


def test_app_swagger_url(aiohttp_app):
    def safe_url_for(route):
        try:
            return route.url_for()
        except KeyError:
            return None

    urls = [safe_url_for(route) for route in aiohttp_app.app.router.routes()]
    assert URL("/v1/api/docs/api-docs") in urls


async def test_app_swagger_json(aiohttp_app):
    resp = await aiohttp_app.get("/v1/api/docs/api-docs")
    docs = await resp.json()

    assert docs["info"]["title"] == "API documentation"
    assert docs["info"]["version"] == "0.0.1"

    openapi_version = docs.get("openapi") or "2.0"
    if openapi_version in SCHEMAS_MAPPING:
        test_schema, class_echo_schema, definitions_schema = SCHEMAS_MAPPING[
            openapi_version
        ]
        docs["paths"]["/v1/test"]["get"]["parameters"] = sorted(
            docs["paths"]["/v1/test"]["get"]["parameters"], key=lambda x: x["name"]
        )
        assert json.dumps(
            docs["paths"]["/v1/test"]["get"], sort_keys=True
        ) == json.dumps(test_schema, sort_keys=True)

        docs["paths"]["/v1/class_echo"]["get"]["parameters"] = sorted(
            docs["paths"]["/v1/class_echo"]["get"]["parameters"],
            key=lambda x: x["name"],
        )
        assert json.dumps(
            docs["paths"]["/v1/class_echo"]["get"], sort_keys=True
        ) == json.dumps(class_echo_schema, sort_keys=True)

        assert json.dumps(docs["definitions"], sort_keys=True) == json.dumps(
            definitions_schema, sort_keys=True
        )
