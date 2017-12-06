import pytest
from aiohttp import web

from aiohttp_apispec import docs


class TestDocumentation:

    @pytest.fixture
    def aiohttp_app(self, doc):
        @docs(tags=['mytag'],
              summary='Test method summary',
              description='Test method description')
        def index(request):
            return web.json_response({'msg': 'done', 'data': {}})

        app = web.Application()
        app.router.add_get('/v1/test', index)

        doc.register(app)

        return app

    def test_app_swagger_url(self, aiohttp_app):
        assert '/api/docs/api-docs' in [route.url() for route in aiohttp_app.router.routes()]

    def test_app_swagger_json(self, aiohttp_app, doc):
        docs = aiohttp_app['swagger_dict']
        assert docs == doc.swagger_dict()
        assert docs['info']['title'] == 'My Documentation'
        assert docs['info']['version'] == 'v1'
        assert docs['paths']['/v1/test']['get'] == {
            'parameters': [],
            'responses': {},
            'tags': ['mytag'],
            'summary': 'Test method summary',
            'description': 'Test method description',
            'produces': ['application/json']
        }
