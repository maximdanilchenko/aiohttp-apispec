import copy

from aiohttp import web
from apispec import APISpec, Path

from .utils import get_path, get_path_keys

PATHS = {'get', 'put', 'post', 'delete', 'patch'}


class AiohttpApiSpec:

    def __init__(self, url='/api/docs/api-docs', **kwargs):
        self.spec = APISpec(**kwargs)
        if 'apispec.ext.marshmallow' not in self.spec.plugins:
            self.spec.setup_plugin('apispec.ext.marshmallow')
        self.url = url

    def swagger_dict(self):
        return self.spec.to_dict()

    def register(self, app: web.Application):
        for route in app.router.routes():
            self._register_route(route)
        app['swagger_dict'] = self.swagger_dict()

        def swagger_handler(request):
            return web.json_response(request.app['swagger_dict'])

        app.router.add_routes([web.get(self.url, swagger_handler)])

    def _register_route(self, route: web.RouteDef):
        view = route.handler
        method = route.method.lower()

        if not hasattr(view, '__apispec__'
                       ) or view.__apispec__['docked'].get(method) is True:
            return None

        view.__apispec__['docked'][method] = True

        url_path = get_path(route)
        if not url_path:
            return None

        if not view.__apispec__['docked'].get('parameters'):
            view.__apispec__['parameters'].extend(
                {"in": "path",
                 "name": path_key,
                 "required": True,
                 "type": "string"}
                for path_key in
                get_path_keys(url_path))
            view.__apispec__['docked']['parameters'] = True
        self._update_paths(view.__apispec__, method, url_path)

    def _update_paths(self,
                      data: dict,
                      method: str,
                      url_path: str):
        operations = copy.deepcopy(data)
        operations.pop('docked', None)

        if method in PATHS:
            self.spec.add_path(Path(path=url_path,
                                    operations={method: operations}))
