import asyncio

import pytest
from aiohttp import web

from aiohttp_apispec import (docs,
                             use_kwargs,
                             marshal_with,
                             aoihttp_apispec_middleware)


class TestViewDecorators:

    @pytest.fixture
    def aiohttp_app(self, doc, request_schema, response_schema, loop, test_client):
        @docs(tags=['mytag'],
              summary='Test method summary',
              description='Test method description')
        @use_kwargs(request_schema, location='query')
        @marshal_with(response_schema, 200)
        def index(request):
            return web.json_response({'msg': 'done', 'data': {}})

        def other(request):
            return web.Response()

        app = web.Application()
        app.router.add_get('/v1/test', index)
        app.router.add_get('/v1/other', other)
        app.middlewares.append(aoihttp_apispec_middleware)
        doc.register(app)

        return loop.run_until_complete(test_client(app))

    @asyncio.coroutine
    def test_response_200(self, aiohttp_app):
        res = yield from aiohttp_app.get('/v1/test', params={'id': 1, 'name': 'max'})
        assert res.status == 200

    @asyncio.coroutine
    def test_response_not_docked(self, aiohttp_app):
        res = yield from aiohttp_app.get('/v1/other', params={'id': 1, 'name': 'max'})
        assert res.status == 200

    @asyncio.coroutine
    def test_response_400(self, aiohttp_app):
        res = yield from aiohttp_app.get('/v1/test', params={'id': 'string', 'name': 'max'})
        assert res.status == 400
