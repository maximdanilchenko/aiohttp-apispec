import pytest
from aiohttp import web

from aiohttp_apispec import docs, request_schema, response_schema


class TestViewDecorators:
    @pytest.fixture
    def aiohttp_view_all(self, request_schema_fixture, response_schema_fixture):
        @docs(
            tags=["mytag"],
            summary="Test method summary",
            description="Test method description",
        )
        @request_schema(request_schema_fixture, locations=["query"])
        @response_schema(response_schema_fixture, 200)
        async def index(request, **data):
            return web.json_response({"msg": "done", "data": {}})

        return index

    @pytest.fixture
    def aiohttp_view_docs(self):
        @docs(
            tags=["mytag"],
            summary="Test method summary",
            description="Test method description",
        )
        async def index(request, **data):
            return web.json_response({"msg": "done", "data": {}})

        return index

    @pytest.fixture
    def aiohttp_view_kwargs(self, request_schema_fixture):
        @request_schema(request_schema_fixture, locations=["query"])
        async def index(request, **data):
            return web.json_response({"msg": "done", "data": {}})

        return index

    @pytest.fixture
    def aiohttp_view_marshal(self, response_schema_fixture):
        @response_schema(response_schema_fixture, 200, description="Method description")
        async def index(request, **data):
            return web.json_response({"msg": "done", "data": {}})

        return index

    def test_docs_view(self, aiohttp_view_docs):
        assert hasattr(aiohttp_view_docs, "__apispec__")
        assert aiohttp_view_docs.__apispec__["tags"] == ["mytag"]
        assert aiohttp_view_docs.__apispec__["summary"] == "Test method summary"
        assert aiohttp_view_docs.__apispec__["description"] == "Test method description"
        for param in ("parameters", "responses"):
            assert param in aiohttp_view_docs.__apispec__

    def test_request_schema_view(self, aiohttp_view_kwargs, request_schema_fixture):
        assert hasattr(aiohttp_view_kwargs, "__apispec__")
        assert hasattr(aiohttp_view_kwargs, "__schemas__")
        assert aiohttp_view_kwargs.__schemas__ == [
            {"schema": request_schema_fixture, "locations": ["query"]}
        ]
        for param in ("parameters", "responses"):
            assert param in aiohttp_view_kwargs.__apispec__

    @pytest.mark.skip
    def test_request_schema_parameters(self, aiohttp_view_kwargs):
        parameters = aiohttp_view_kwargs.__apispec__["parameters"]
        assert sorted(parameters, key=lambda x: x["name"]) == [
            {"in": "query", "name": "bool_field", "required": False, "type": "boolean"},
            {
                "in": "query",
                "name": "id",
                "required": False,
                "type": "integer",
                "format": "int32",
            },
            {
                "in": "query",
                "name": "list_field",
                "required": False,
                "collectionFormat": "multi",
                "type": "array",
                "items": {"type": "integer", "format": "int32"},
            },
            {
                "in": "query",
                "name": "name",
                "required": False,
                "type": "string",
                "description": "name",
            },
        ]

    def test_marshalling(self, aiohttp_view_marshal):
        assert hasattr(aiohttp_view_marshal, "__apispec__")
        for param in ("parameters", "responses"):
            assert param in aiohttp_view_marshal.__apispec__
        assert "200" in aiohttp_view_marshal.__apispec__["responses"]

    def test_all(self, aiohttp_view_all):
        assert hasattr(aiohttp_view_all, "__apispec__")
        assert hasattr(aiohttp_view_all, "__schemas__")
        for param in ("parameters", "responses"):
            assert param in aiohttp_view_all.__apispec__
        assert aiohttp_view_all.__apispec__["tags"] == ["mytag"]
        assert aiohttp_view_all.__apispec__["summary"] == "Test method summary"
        assert aiohttp_view_all.__apispec__["description"] == "Test method description"

    def test_view_multiple_body_parameters(self, request_schema_fixture):
        with pytest.raises(RuntimeError) as ex:

            @request_schema(request_schema_fixture, locations=["body"])
            @request_schema(request_schema_fixture, locations=["body"])
            async def index(request, **data):
                return web.json_response({"msg": "done", "data": {}})

        assert isinstance(ex.value, RuntimeError)
        assert str(ex.value) == "Multiple body parameters are not allowed"
