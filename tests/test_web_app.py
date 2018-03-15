import asyncio

import pytest
from aiohttp import web

from aiohttp_apispec import use_kwargs, aoihttp_apispec_middleware


class TestViewDecorators:

    @pytest.fixture
    def aiohttp_app(self, doc, request_schema, loop, test_client):
        @use_kwargs(request_schema, location='query')
        def handler_get(request):
            print(request.data)
            return web.json_response({'msg': 'done', 'data': {}})

        @use_kwargs(request_schema)
        def handler_post(request):
            print(request.data)
            return web.json_response({'msg': 'done', 'data': {}})

        @use_kwargs(request_schema)
        def handler_echo(request):
            return web.json_response(request.data)

        def other(request):
            return web.Response()

        app = web.Application()
        app.router.add_routes([
            web.get('/v1/test', handler_get),
            web.post('/v1/test', handler_post)])
        # app.router.add_get('/v1/test', handler_get)
        # app.router.add_post('/v1/test', handler_post)
        app.router.add_get('/v1/other', other)
        app.router.add_post('/v1/echo', handler_echo)
        app.middlewares.append(aoihttp_apispec_middleware)
        doc.register(app)

        return loop.run_until_complete(test_client(app))

    @asyncio.coroutine
    def test_response_200_get(self, aiohttp_app):
        res = yield from aiohttp_app.get('/v1/test', params={'id': 1, 'name': 'max'})
        assert res.status == 200

    @asyncio.coroutine
    def test_response_400_get(self, aiohttp_app):
        res = yield from aiohttp_app.get('/v1/test', params={'id': 'string', 'name': 'max'})
        assert res.status == 400

    @asyncio.coroutine
    def test_response_200_post(self, aiohttp_app):
        res = yield from aiohttp_app.post('/v1/test', json={'id': 1, 'name': 'max'})
        assert res.status == 200

    @asyncio.coroutine
    def test_response_400_post(self, aiohttp_app):
        res = yield from aiohttp_app.post('/v1/test', json={'id': 'string', 'name': 'max'})
        assert res.status == 400

    @asyncio.coroutine
    def test_response_not_docked(self, aiohttp_app):
        res = yield from aiohttp_app.get('/v1/other', params={'id': 1, 'name': 'max'})
        assert res.status == 200

    @asyncio.coroutine
    def test_response_data(self, aiohttp_app):
        res = yield from aiohttp_app.post('/v1/echo', json={'id': 1, 'name': 'max'})
        assert (yield from res.json()) == {'id': 1, 'name': 'max'}

    @asyncio.coroutine
    def test_swagger_handler_200(self, aiohttp_app):
        res = yield from aiohttp_app.get('/api/docs/api-docs')
        assert res.status == 200
        assert aiohttp_app.server.app['swagger_dict'] == (yield from res.json())
