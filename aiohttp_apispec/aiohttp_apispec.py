import copy

from aiohttp import web
from aiohttp.hdrs import METH_ANY, METH_ALL
from apispec import APISpec, Path

from .utils import get_path, get_path_keys

PATHS = {'get', 'put', 'post', 'delete', 'patch'}


def issubclass_py37fix(cls, cls_info):
    try:
        return issubclass(cls, cls_info)
    except TypeError:
        return False


class AiohttpApiSpec:
    """
    Aiohttp-apispec extension. Add app param to register all routes on startup.

    Usage:

    .. code-block:: python

        from aiohttp_apispec import docs, use_kwargs, AiohttpApiSpec
        from aiohttp import web
        from marshmallow import Schema, fields


        class RequestSchema(Schema):
            id = fields.Int()
            name = fields.Str(description='name')
            bool_field = fields.Bool()


        @docs(tags=['mytag'],
              summary='Test method summary',
              description='Test method description')
        @use_kwargs(RequestSchema)
        async def index(request):
            return web.json_response({'msg': 'done', 'data': {}})


        app = web.Application()
        app.router.add_post('/v1/test', index)

        # init docs with all parameters, usual for ApiSpec
        doc = AiohttpApiSpec(app=app,
                             title='My Documentation',
                             version='v1',
                             url='/api/docs/api-docs')

        # now we can find it on 'http://localhost:8080/api/docs/api-docs'
        web.run_app(app)

    :param Application app: aiohttp web app
    :param url: url for swagger spec in JSON format
    :param kwargs: any APISpec kwargs
    """

    def __init__(self, url='/api/docs/api-docs', app=None, **kwargs):
        self.spec = APISpec(**kwargs)
        if 'apispec.ext.marshmallow' not in self.spec.plugins:
            self.spec.setup_plugin('apispec.ext.marshmallow')
        self.url = url
        self._registered = False
        if app is not None:
            self.register(app)

    def swagger_dict(self):
        return self.spec.to_dict()

    def register(self, app: web.Application):
        """
        Register all aiohttp app views

        Usage:

        .. code-block:: python

            doc = AiohttpApiSpec(title='My Documentation',
                                 version='v1',
                                 url='/api/docs/api-docs')
            # we should do it only after all routes are added to router!
            doc.register(app)

        :param Application app: aiohttp web app
        """
        if self._registered is True:
            return None

        async def doc_routes(app_):
            self._register(app_)

        app.on_startup.append(doc_routes)
        self._registered = True

        def swagger_handler(request):
            return web.json_response(request.app['swagger_dict'])

        app.router.add_routes([web.get(self.url, swagger_handler)])

    def _register(self, app: web.Application):
        for route in app.router.routes():
            if issubclass_py37fix(route.handler, web.View) and route.method == METH_ANY:
                for attr in dir(route.handler):
                    if attr.upper() in METH_ALL:
                        view = getattr(route.handler, attr)
                        method = attr
                        self._register_route(route, method, view)
            else:
                method = route.method.lower()
                view = route.handler
                self._register_route(route, method, view)
        app['swagger_dict'] = self.swagger_dict()

    def _register_route(self, route: web.RouteDef, method, view):

        if (
            not hasattr(view, '__apispec__')
            or view.__apispec__['docked'].get(method) is True
        ):
            return None

        view.__apispec__['docked'][method] = True

        url_path = get_path(route)
        if not url_path:
            return None

        if not view.__apispec__['docked'].get('parameters'):
            view.__apispec__['parameters'].extend(
                {"in": "path", "name": path_key, "required": True, "type": "string"}
                for path_key in get_path_keys(url_path)
            )
            view.__apispec__['docked']['parameters'] = True
        self._update_paths(view.__apispec__, method, url_path)

    def _update_paths(self, data: dict, method: str, url_path: str):
        operations = copy.deepcopy(data)
        operations.pop('docked', None)

        if method in PATHS:
            self.spec.add_path(Path(path=url_path, operations={method: operations}))
