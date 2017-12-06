import copy

from aiohttp import web
from apispec import APISpec, Path

from .utils import get_path, get_path_keys

PATHS = {'get', 'put', 'post', 'delete', 'patch'}


class AiohttpApiSpec:
    def __init__(self, url='/api/docs/api-docs', **kwargs):
        self.spec = APISpec(**kwargs, plugins=('apispec.ext.marshmallow',))
        self.url = url

    def swagger_dict(self):
        return self.spec.to_dict()

    def register(self, app: web.Application, ):
        for route in app.router.routes():
            view = route.handler
            method = route.method.lower()
            if hasattr(view, '__apispec__'
                       ) and view.__apispec__['docked'].get(method) is not True:
                url_path = get_path(route)
                if url_path:
                    if not view.__apispec__['docked'].get('parameters'):
                        view.__apispec__['parameters'].extend({"in": "path",
                                                               "name": path_key,
                                                               "required": True,
                                                               "type": "string"}
                                                              for path_key in
                                                              get_path_keys(url_path))
                        view.__apispec__['docked']['parameters'] = True
                    self._update_paths(view.__apispec__, method, url_path)
                view.__apispec__['docked'][method] = True
        app['swagger_dict'] = self.spec.to_dict()

        def swagger_handler(request):
            return web.json_response(request.app['swagger_dict'])

        app.router.add_routes([web.get(self.url, swagger_handler)])

    def _update_paths(self, data: dict, method, url_path):
        operations = copy.deepcopy(data)
        operations.pop('docked', None)

        if method in PATHS:
            self.spec.add_path(Path(path=url_path, operations={method: operations}))
