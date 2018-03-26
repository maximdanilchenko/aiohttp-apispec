import asyncio

import pytest
from aiohttp import web

from aiohttp_apispec import use_kwargs, aiohttp_apispec_middleware


class TestViewDecorators:

    @pytest.fixture(params=[{'locations': ['query']}, {'location': 'query'}])
    def aiohttp_app(self, doc, request_schema, request_callable_schema, loop, test_client, request):
        @use_kwargs(request_schema, **request.param)
        def handler_get(request):
            print(request.data)
            return web.json_response({'msg': 'done', 'data': {}})

        @use_kwargs(request_schema)
        def handler_post(request):
            print(request.data)
            return web.json_response({'msg': 'done', 'data': {}})

        @use_kwargs(request_callable_schema)
        def handler_post_callable_schema(request):
            print(request.data)
            return web.json_response({'msg': 'done', 'data': {}})

        @use_kwargs(request_schema)
        def handler_post_echo(request):
            return web.json_response(request['data'])

        @use_kwargs(request_schema, **request.param)
        def handler_get_echo(request):
            print(request.data)
            return web.json_response(request['data'])

        @use_kwargs(request_schema, **request.param)
        def handler_get_echo_old_data(request):
            print(request.data)
            return web.json_response(request.data)

        def other(request):
            return web.Response()

        app = web.Application()
        app.router.add_routes([
            web.get('/v1/test', handler_get),
            web.post('/v1/test', handler_post),
            web.post('/v1/test_call', handler_post_callable_schema),
            web.get('/v1/other', other),
            web.get('/v1/echo', handler_get_echo),
            web.get('/v1/echo_old', handler_get_echo_old_data),
            web.post('/v1/echo', handler_post_echo),
        ])
        app.middlewares.append(aiohttp_apispec_middleware)
        doc.register(app)

        return loop.run_until_complete(test_client(app))

    @asyncio.coroutine
    def test_response_200_get(self, aiohttp_app):
        res = yield from aiohttp_app.get('/v1/test', params={'id': 1, 'name': 'max'})
        assert res.status == 200

    @asyncio.coroutine
    def test_response_422_get(self, aiohttp_app):
        res = yield from aiohttp_app.get('/v1/test', params={'id': 'string', 'name': 'max'})
        assert res.status == 400

    @asyncio.coroutine
    def test_response_200_post(self, aiohttp_app):
        res = yield from aiohttp_app.post('/v1/test', json={'id': 1, 'name': 'max'})
        assert res.status == 200

    @asyncio.coroutine
    def test_response_200_post_callable_schema(self, aiohttp_app):
        res = yield from aiohttp_app.post('/v1/test_call', json={'id': 1, 'name': 'max'})
        assert res.status == 200

    @asyncio.coroutine
    def test_response_422_post(self, aiohttp_app):
        res = yield from aiohttp_app.post('/v1/test', json={'id': 'string', 'name': 'max'})
        assert res.status == 400

    @asyncio.coroutine
    def test_response_not_docked(self, aiohttp_app):
        res = yield from aiohttp_app.get('/v1/other', params={'id': 1, 'name': 'max'})
        assert res.status == 200

    @asyncio.coroutine
    def test_response_data_post(self, aiohttp_app):
        res = yield from aiohttp_app.post('/v1/echo', json={'id': 1, 'name': 'max',
                                                            'list_field': [1, 2, 3, 4]})
        assert (yield from res.json()) == {'id': 1, 'name': 'max', 'list_field': [1, 2, 3, 4]}

    @asyncio.coroutine
    def test_response_data_get_old_data(self, aiohttp_app):
        res = yield from aiohttp_app.get('/v1/echo_old', params=[('id', '1'),
                                                                 ('name', 'max'),
                                                                 ('bool_field', '0'),
                                                                 ('list_field', '1'),
                                                                 ('list_field', '2'),
                                                                 ('list_field', '3'),
                                                                 ('list_field', '4')])
        assert (yield from res.json()) == {'id': 1, 'name': 'max', 'bool_field': False, 'list_field': [1, 2, 3, 4]}

    @asyncio.coroutine
    def test_response_data_get(self, aiohttp_app):
        res = yield from aiohttp_app.get('/v1/echo', params=[('id', '1'),
                                                             ('name', 'max'),
                                                             ('bool_field', '0'),
                                                             ('list_field', '1'),
                                                             ('list_field', '2'),
                                                             ('list_field', '3'),
                                                             ('list_field', '4')])
        assert (yield from res.json()) == {'id': 1, 'name': 'max', 'bool_field': False, 'list_field': [1, 2, 3, 4]}

    @asyncio.coroutine
    def test_swagger_handler_200(self, aiohttp_app):
        res = yield from aiohttp_app.get('/api/docs/api-docs')
        assert res.status == 200
        assert aiohttp_app.server.app['swagger_dict'] == (yield from res.json())
