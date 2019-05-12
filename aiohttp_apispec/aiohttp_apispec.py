import copy
from pathlib import Path
from typing import Callable, Awaitable

from aiohttp import web
from aiohttp.hdrs import METH_ANY, METH_ALL
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from jinja2 import Template

from .utils import get_path, get_path_keys, issubclass_py37fix

PATHS = {"get", "put", "post", "delete", "patch"}

_AiohttpView = Callable[[web.Request], Awaitable[web.StreamResponse]]

VALID_RESPONSE_FIELDS = {"schema", "description", "headers", "examples"}


class AiohttpApiSpec:
    def __init__(
        self,
        url="/api/docs/swagger.json",
        app=None,
        request_data_name="data",
        swagger_path=None,
        static_path="/static/swagger",
        **kwargs
    ):

        self.plugin = MarshmallowPlugin()
        self.spec = APISpec(plugins=(self.plugin,), **kwargs)

        self.url = url
        self.swagger_path = swagger_path
        self.static_path = static_path
        self._registered = False
        self._request_data_name = request_data_name
        if app is not None:
            self.register(app)

    def swagger_dict(self):
        return self.spec.to_dict()

    def register(self, app: web.Application):
        if self._registered is True:
            return None
        app["_apispec_request_data_name"] = self._request_data_name

        async def doc_routes(app_):
            self._register(app_)

        app.on_startup.append(doc_routes)
        self._registered = True

        async def swagger_handler(request):
            return web.json_response(request.app["swagger_dict"])

        app.router.add_routes([web.get(self.url, swagger_handler)])

        if self.swagger_path is not None:
            self.add_swagger_web_page(app, self.static_path, self.swagger_path)

    def add_swagger_web_page(
        self, app: web.Application, static_path: str, view_path: str
    ):
        static_files = Path(__file__).parent / "static"
        app.router.add_static(static_path, static_files)

        with open(str(static_files / "index.html")) as swg_tmp:
            tmp = Template(swg_tmp.read()).render(path=self.url, static=static_path)

        async def swagger_view(_):
            return web.Response(text=tmp, content_type="text/html")

        app.router.add_route("GET", view_path, swagger_view)

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
        app["swagger_dict"] = self.swagger_dict()

    def _register_route(
        self, route: web.AbstractRoute, method: str, view: _AiohttpView
    ):

        if not hasattr(view, "__apispec__"):
            return None

        url_path = get_path(route)
        if not url_path:
            return None

        self._update_paths(view.__apispec__, method, url_path)

    def _update_paths(self, data: dict, method: str, url_path: str):
        if method not in PATHS:
            return None
        if "schema" in data:
            parameters = self.plugin.openapi.schema2parameters(
                data.pop("schema"), **data.pop("options")
            )
            data["parameters"].extend(parameters)

        existing = [p["name"] for p in data["parameters"] if p["in"] == "path"]
        data["parameters"].extend(
            {"in": "path", "name": path_key, "required": True, "type": "string"}
            for path_key in get_path_keys(url_path)
            if path_key not in existing
        )

        if "responses" in data:
            responses = {}
            for code, params in data["responses"].items():
                if "schema" in params:
                    raw_parameters = self.plugin.openapi.schema2parameters(
                        params["schema"], required=params.get("required", False)
                    )[0]
                    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#responseObject
                    parameters = {
                        k: v
                        for k, v in raw_parameters.items()
                        if k in VALID_RESPONSE_FIELDS
                    }
                    for extra_info in ("description", "headers", "examples"):
                        if extra_info in params:
                            parameters[extra_info] = params[extra_info]
                    responses[code] = parameters
                else:
                    responses[code] = params
            data["responses"] = responses

        operations = copy.deepcopy(data)
        self.spec.path(path=url_path, operations={method: operations})


def setup_aiohttp_apispec(
    app: web.Application,
    *,
    title: str = "API documentation",
    version: str = "0.0.1",
    openapi_version: str = "2.0",
    url: str = "/api/docs/swagger.json",
    request_data_name: str = "data",
    swagger_path: str = None,
    static_path: str = "/static/swagger",
    **kwargs
) -> None:
    """
    aiohttp-apispec extension.

    Usage:

    .. code-block:: python

        from aiohttp_apispec import docs, request_schema, setup_aiohttp_apispec
        from aiohttp import web
        from marshmallow import Schema, fields


        class RequestSchema(Schema):
            id = fields.Int()
            name = fields.Str(description='name')
            bool_field = fields.Bool()


        @docs(tags=['mytag'],
              summary='Test method summary',
              description='Test method description')
        @request_schema(RequestSchema)
        async def index(request):
            return web.json_response({'msg': 'done', 'data': {}})


        app = web.Application()
        app.router.add_post('/v1/test', index)

        # init docs with all parameters, usual for ApiSpec
        setup_aiohttp_apispec(app=app,
                              title='My Documentation',
                              version='v1',
                              url='/api/docs/api-docs')

        # now we can find it on 'http://localhost:8080/api/docs/api-docs'
        web.run_app(app)

    :param Application app: aiohttp web app
    :param str title: API title
    :param str version: API version
    :param str openapi_version: OpenAPI version to use. By default: ``'2.0'``
    :param str url: url for swagger spec in JSON format
    :param str request_data_name: name of the key in Request object
                                  where validated data will be placed by
                                  validation_middleware (``'data'`` by default)
    :param str swagger_path: experimental SwaggerUI support (starting from v1.1.0).
                             By default it is None (disabled)
    :param str static_path: path for static files used by SwaggerUI
                            (if it is enabled with ``swagger_path``)
    :param kwargs: any apispec.APISpec kwargs
    """
    AiohttpApiSpec(
        url,
        app,
        request_data_name,
        title=title,
        version=version,
        openapi_version=openapi_version,
        swagger_path=swagger_path,
        static_path=static_path,
        **kwargs
    )
