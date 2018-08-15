import pytest
from aiohttp import web
from yarl import URL
from aiohttp_apispec import docs, AiohttpApiSpec


class TestDocumentation:
    @pytest.fixture(params=[{'register_twice': True}, {'register_twice': False}])
    def aiohttp_app(self, loop, test_client, request):
        @docs(
            tags=['mytag'],
            summary='Test method summary',
            description='Test method description',
        )
        def index(request):
            return web.json_response({'msg': 'done', 'data': {}})

        class TheView(web.View):
            @docs(
                tags=['mytag'],
                summary='View method summary',
                description='View method description',
            )
            def delete(self):
                return web.Response()

        app = web.Application()
        doc = AiohttpApiSpec(
            app=app, title='My Documentation', version='v1', url='/api/docs/api-docs'
        )

        app.router.add_get('/v1/test', index)
        app.router.add_view('/v1/view', TheView)
        if request.param['register_twice']:
            doc.register(app)
        return loop.run_until_complete(test_client(app))

    def test_app_swagger_url(self, aiohttp_app):
        assert URL('/api/docs/api-docs') in [
            route.url_for() for route in aiohttp_app.app.router.routes()
        ]

    def test_app_swagger_json(self, aiohttp_app):
        docs = aiohttp_app.app['swagger_dict']
        assert docs['info']['title'] == 'My Documentation'
        assert docs['info']['version'] == 'v1'
        assert docs['paths']['/v1/test']['get'] == {
            'parameters': [],
            'responses': {},
            'tags': ['mytag'],
            'summary': 'Test method summary',
            'description': 'Test method description',
            'produces': ['application/json'],
        }
        assert docs['paths']['/v1/view']['delete'] == {
            'parameters': [],
            'responses': {},
            'tags': ['mytag'],
            'summary': 'View method summary',
            'description': 'View method description',
            'produces': ['application/json'],
        }
