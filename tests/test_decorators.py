import pytest
from aiohttp import web

from aiohttp_apispec import docs, use_kwargs, marshal_with


class TestViewDecorators:
    @pytest.fixture
    def aiohttp_view_all(self, request_schema, response_schema):
        @docs(
            tags=['mytag'],
            summary='Test method summary',
            description='Test method description',
        )
        @use_kwargs(request_schema, locations=['query'])
        @marshal_with(response_schema, 200)
        def index(request, **data):
            return web.json_response({'msg': 'done', 'data': {}})

        return index

    @pytest.fixture
    def aiohttp_view_docs(self):
        @docs(
            tags=['mytag'],
            summary='Test method summary',
            description='Test method description',
        )
        def index(request, **data):
            return web.json_response({'msg': 'done', 'data': {}})

        return index

    @pytest.fixture
    def aiohttp_view_kwargs(self, request_schema):
        @use_kwargs(request_schema, locations=['query'])
        def index(request, **data):
            return web.json_response({'msg': 'done', 'data': {}})

        return index

    @pytest.fixture
    def aiohttp_view_marshal(self, response_schema):
        @marshal_with(response_schema, 200, description='Method description')
        def index(request, **data):
            return web.json_response({'msg': 'done', 'data': {}})

        return index

    def test_docs_view(self, aiohttp_view_docs):
        assert hasattr(aiohttp_view_docs, '__apispec__')
        assert aiohttp_view_docs.__apispec__['tags'] == ['mytag']
        assert aiohttp_view_docs.__apispec__['summary'] == 'Test method summary'
        assert aiohttp_view_docs.__apispec__['description'] == 'Test method description'
        for param in ('parameters', 'responses', 'docked'):
            assert param in aiohttp_view_docs.__apispec__
        assert aiohttp_view_docs.__apispec__['docked'] == {'route': False}

    def test_use_kwargs_view(self, aiohttp_view_kwargs, request_schema):
        assert hasattr(aiohttp_view_kwargs, '__apispec__')
        assert hasattr(aiohttp_view_kwargs, '__schemas__')
        assert aiohttp_view_kwargs.__schemas__ == [
            {'schema': request_schema, 'locations': ['query']}
        ]
        for param in ('parameters', 'responses', 'docked'):
            assert param in aiohttp_view_kwargs.__apispec__

    def test_use_kwargs_parameters(self, aiohttp_view_kwargs):
        parameters = aiohttp_view_kwargs.__apispec__['parameters']
        print(sorted(parameters, key=lambda x: x['name']))
        assert sorted(parameters, key=lambda x: x['name']) == [
            {'in': 'query', 'name': 'bool_field', 'required': False, 'type': 'boolean'},
            {
                'in': 'query',
                'name': 'id',
                'required': False,
                'type': 'integer',
                'format': 'int32',
            },
            {
                'in': 'query',
                'name': 'list_field',
                'required': False,
                'collectionFormat': 'multi',
                'type': 'array',
                'items': {'type': 'integer', 'format': 'int32'},
            },
            {
                'in': 'query',
                'name': 'name',
                'required': False,
                'type': 'string',
                'description': 'name',
            },
        ]

    def test_marshalling(self, aiohttp_view_marshal):
        assert hasattr(aiohttp_view_marshal, '__apispec__')
        for param in ('parameters', 'responses', 'docked'):
            assert param in aiohttp_view_marshal.__apispec__
        assert '200' in aiohttp_view_marshal.__apispec__['responses']
        assert aiohttp_view_marshal.__apispec__['responses']['200'] == {
            'schema': {
                'type': 'object',
                'properties': {'data': {'type': 'object'}, 'msg': {'type': 'string'}},
            },
            'description': 'Method description',
        }

    def test_all(self, aiohttp_view_all):
        assert hasattr(aiohttp_view_all, '__apispec__')
        assert hasattr(aiohttp_view_all, '__schemas__')
        for param in ('parameters', 'responses', 'docked'):
            assert param in aiohttp_view_all.__apispec__
        assert aiohttp_view_all.__apispec__['tags'] == ['mytag']
        assert aiohttp_view_all.__apispec__['summary'] == 'Test method summary'
        assert aiohttp_view_all.__apispec__['description'] == 'Test method description'
