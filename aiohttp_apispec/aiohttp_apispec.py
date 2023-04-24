import copy
import enum
import json
import os
from pathlib import Path
from typing import Awaitable, Callable, Union

from aiohttp import web
from aiohttp.hdrs import METH_ALL, METH_ANY
from apispec import APISpec
from apispec.core import VALID_METHODS_OPENAPI_V2
from apispec.ext.marshmallow import MarshmallowPlugin, common
from jinja2 import Template
from webargs.aiohttpparser import parser

from .utils import get_path, get_path_keys, issubclass_py37fix

_AiohttpView = Callable[[web.Request], Awaitable[web.StreamResponse]]

VALID_RESPONSE_FIELDS = {"description", "headers", "examples"}

DEFAULT_RESPONSE_LOCATION = "json"

NAME_SWAGGER_SPEC = "swagger.spec"
NAME_SWAGGER_DOCS = "swagger.docs"
NAME_SWAGGER_STATIC = "swagger.static"

INDEX_PAGE = "index.html"


def resolver(schema):
    schema_instance = common.resolve_schema_instance(schema)
    prefix = "Partial-" if schema_instance.partial else ""
    schema_cls = common.resolve_schema_cls(schema)
    name = prefix + schema_cls.__name__
    if name.endswith("Schema"):
        return name[:-6] or name
    return name


class OpenApiVersion(str, enum.Enum):
    V20 = "2.0"
    V300 = "3.0.0"
    V301 = "3.0.1"
    V302 = "3.0.2"
    V303 = "3.0.3"


class AiohttpApiSpec:
    def __init__(
        self,
        url="/api/docs/swagger.json",
        app=None,
        request_data_name="data",
        swagger_path=None,
        static_path='/static/swagger',
        error_callback=None,
        in_place=False,
        prefix='',
        schema_name_resolver=resolver,
        openapi_version=None,
        **kwargs,
    ):
        openapi_version = openapi_version or OpenApiVersion.V20
        try:
            openapi_version = OpenApiVersion(openapi_version)
        except ValueError:
            raise ValueError(
                f"Invalid `openapi_version`: {openapi_version!r}"
            ) from None

        self.plugin = MarshmallowPlugin(schema_name_resolver=schema_name_resolver)
        self.spec = APISpec(
            plugins=(self.plugin,),
            openapi_version=openapi_version.value,
            **kwargs,
        )

        self.url = url
        self.swagger_path = swagger_path
        self.static_path = static_path
        self._registered = False
        self._request_data_name = request_data_name
        self.error_callback = error_callback
        self.prefix = prefix
        self._index_page = None
        if app is not None:
            self.register(app, in_place)

    def swagger_dict(self):
        """Returns swagger spec representation in JSON format"""
        return self.spec.to_dict()

    def register(self, app: web.Application, in_place: bool = False):
        """Creates spec based on registered app routes and registers needed view"""
        if self._registered is True:
            return None

        app["_apispec_request_data_name"] = self._request_data_name

        if self.error_callback:
            parser.error_callback = self.error_callback
        app["_apispec_parser"] = parser

        if in_place:
            self._register(app)
        else:

            async def doc_routes(app_):
                self._register(app_)

            app.on_startup.append(doc_routes)

        self._registered = True

        if self.url is not None:

            async def swagger_handler(request):
                return web.json_response(request.app["swagger_dict"])

            route_url = self.url
            if not self.url.startswith("/"):
                route_url = "/{}".format(self.url)
            app.router.add_route(
                "GET", route_url, swagger_handler, name=NAME_SWAGGER_SPEC
            )

            if self.swagger_path is not None:
                self._add_swagger_web_page(app, self.static_path, self.swagger_path)

    def _get_index_page(self, app, static_files, static_path):
        if self._index_page is not None:
            return self._index_page

        with open(str(static_files / INDEX_PAGE)) as swg_tmp:
            url = self.url if app is None else app.router[NAME_SWAGGER_SPEC].url_for()

            if app is not None:
                static_path = app.router[NAME_SWAGGER_STATIC].url_for(
                    filename=INDEX_PAGE
                )
                static_path = os.path.dirname(str(static_path))

            if not self.spec.options.get("display_configurations"):
                self.spec.options["display_configurations"] = {}

            self._index_page = Template(swg_tmp.read()).render(
                path=url,
                static=static_path,
                display_configurations=json.dumps(
                    self.spec.options["display_configurations"]
                ),
            )

        return self._index_page

    def _add_swagger_web_page(
        self, app: web.Application, static_path: str, view_path: str
    ):
        static_files = Path(__file__).parent / "static"
        app.router.add_static(static_path, static_files, name=NAME_SWAGGER_STATIC)

        async def swagger_view(_):
            index_page = self._get_index_page(app, static_files, static_path)
            return web.Response(text=index_page, content_type="text/html")

        app.router.add_route("GET", view_path, swagger_view, name=NAME_SWAGGER_DOCS)

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

        self._update_paths(view.__apispec__, method, self.prefix + url_path)

    def _update_paths(self, data: dict, method: str, url_path: str):
        if method not in VALID_METHODS_OPENAPI_V2:
            return None
        for schema in data.pop("schemas", []):
            if (
                self.spec.components.openapi_version.major > 2
                and self._is_body_location(schema["location"])
            ):
                # in OpenAPI 3.0 in=body parameters must be put into requestBody
                # https://apispec.readthedocs.io/en/latest/api_ext.html#apispec.ext.marshmallow.openapi.OpenAPIConverter.schema2parameters
                # lets reinvent something that works, because apispec doesn't provide anything with which we could work
                body = dict(**schema["options"])
                body["schema"] = self.plugin.converter.resolve_nested_schema(
                    schema["schema"]
                )
                self._add_examples(schema["schema"], [body], schema["example"])
                data["requestBody"] = {
                    "content": {
                        self._content_type(schema["location"]): body,
                    },
                }
            else:
                parameters = self.plugin.converter.schema2parameters(
                    schema["schema"], location=schema["location"], **schema["options"]
                )
                self._add_examples(schema["schema"], parameters, schema["example"])
                data["parameters"].extend(parameters)

        existing = [p["name"] for p in data["parameters"] if p["in"] == "path"]
        data["parameters"].extend(
            {"in": "path", "name": path_key, "required": True, "type": "string"}
            for path_key in get_path_keys(url_path)
            if path_key not in existing
        )

        if "responses" in data:
            responses = {}
            for code, actual_params in data["responses"].items():
                if "schema" in actual_params:
                    raw_parameters = self.plugin.converter.schema2parameters(
                        actual_params["schema"],
                        location=DEFAULT_RESPONSE_LOCATION,
                        required=actual_params.get("required", False),
                    )[0]
                    updated_params = {
                        k: v
                        for k, v in raw_parameters.items()
                        if k in VALID_RESPONSE_FIELDS
                    }
                    if self.spec.components.openapi_version.major < 3:
                        updated_params['schema'] = actual_params["schema"]
                    else:
                        updated_params["content"] = {
                            "application/json": {
                                "schema": actual_params["schema"],
                            },
                        }
                    for extra_info in ("description", "headers", "examples"):
                        if extra_info in actual_params:
                            updated_params[extra_info] = actual_params[extra_info]
                    responses[code] = updated_params
                else:
                    responses[code] = actual_params
            data["responses"] = responses

        operations = copy.deepcopy(data)
        self.spec.path(path=url_path, operations={method: operations})

    def _add_examples(self, ref_schema, endpoint_schema, example):
        def add_to_endpoint_or_ref():
            if add_to_refs:
                self.spec.components.schemas[name]["example"] = example
            else:
                endpoint_schema[0]['schema']['allOf'] = [
                    endpoint_schema[0]['schema'].pop('$ref')
                ]
                endpoint_schema[0]['schema']["example"] = example

        if not example:
            return
        schema_instance = common.resolve_schema_instance(ref_schema)
        name = self.plugin.converter.schema_name_resolver(schema_instance)
        add_to_refs = example.pop('add_to_refs')
        if self.spec.components.openapi_version.major < 3:
            if name and name in self.spec.components.schemas:
                add_to_endpoint_or_ref()
        else:
            add_to_endpoint_or_ref()

    def _content_type(self, location):
        """
        extract body content type from parameters location

        :param location: body location name, e.g. json, form etc
        :return: return valid content-type header
        """
        if not self._is_body_location(location):
            raise ValueError(
                f"Illegal location {location}, cannnot be converted to body"
            )
        if location == "json":
            return "application/json"
        if location == "form":
            return "application/x-www-form-urlencoded"
        # fallback to something generic
        return "application/octet-stream"

    def _is_body_location(self, location):
        """
        check if location is valid body location

        :param location: body location name, e.g. json, form etc
        :return: True in case if location looks like body and False otherwises
        """
        return location in ("files", "form", "json")


def setup_aiohttp_apispec(
    app: web.Application,
    *,
    title: str = "API documentation",
    version: str = "0.0.1",
    url: str = "/api/docs/swagger.json",
    request_data_name: str = "data",
    swagger_path: str = None,
    static_path: str = '/static/swagger',
    error_callback=None,
    in_place: bool = False,
    prefix: str = '',
    schema_name_resolver: Callable = resolver,
    openapi_version: Union[str, OpenApiVersion] = OpenApiVersion.V20,
    **kwargs,
) -> AiohttpApiSpec:
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
    :param str url: url for swagger spec in JSON format
    :param str request_data_name: name of the key in Request object
                                  where validated data will be placed by
                                  validation_middleware (``'data'`` by default)
    :param str swagger_path: experimental SwaggerUI support (starting from v1.1.0).
                             By default it is None (disabled)
    :param str static_path: path for static files used by SwaggerUI
                            (if it is enabled with ``swagger_path``)
    :param error_callback: custom error handler
    :param in_place: register all routes at the moment of calling this function
                     instead of the moment of the on_startup signal.
                     If True, be sure all routes are added to router
    :param prefix: prefix to add to all registered routes
    :param schema_name_resolver: custom schema_name_resolver for MarshmallowPlugin.
    :param openapi_version: version of OpenAPI schema
    :param kwargs: any apispec.APISpec kwargs
    :return: return instance of AiohttpApiSpec class
    :rtype: AiohttpApiSpec
    """
    return AiohttpApiSpec(
        url,
        app,
        request_data_name,
        title=title,
        version=version,
        swagger_path=swagger_path,
        static_path=static_path,
        error_callback=error_callback,
        in_place=in_place,
        prefix=prefix,
        schema_name_resolver=schema_name_resolver,
        openapi_version=openapi_version,
        **kwargs,
    )
