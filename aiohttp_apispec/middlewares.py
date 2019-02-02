import warnings

from aiohttp import web
from webargs.aiohttpparser import parser

from .utils import issubclass_py37fix


@web.middleware
async def validation_middleware(request: web.Request, handler) -> web.Response:
    """
    Validation middleware for aiohttp web app

    Usage:

    .. code-block:: python

        app.middlewares.append(validation_middleware)


    """
    orig_handler = request.match_info.handler
    if not hasattr(orig_handler, "__schemas__"):
        if not issubclass_py37fix(orig_handler, web.View):
            return await handler(request)
        sub_handler = getattr(orig_handler, request.method.lower(), None)
        if sub_handler is None:
            return await handler(request)
        if not hasattr(sub_handler, "__schemas__"):
            return await handler(request)
        schemas = sub_handler.__schemas__
    else:
        schemas = orig_handler.__schemas__
    kwargs = {}
    for schema in schemas:
        data = await parser.parse(
            schema["schema"], request, locations=schema["locations"]
        )
        if data:
            kwargs.update(data)
    kwargs.update(request.match_info)
    # request.data will be removed since 1.0.0
    request[request.app["_apispec_request_data_name"]] = request.data = kwargs
    return await handler(request)


@web.middleware
async def aiohttp_apispec_middleware(
    request: web.Request, handler, error_handler=None
) -> web.Response:
    warnings.warn(
        "'aiohttp_apispec_middleware' will be removed since '1.0.0' version"
        " of 'aiohttp-apispec', use 'validation_middleware' instead",
        PendingDeprecationWarning,
    )

    if not hasattr(handler, "__schemas__"):
        if not issubclass_py37fix(handler, web.View):
            return await handler(request)
        method = request.method.lower()
        if not hasattr(handler, method):
            return await handler(request)
        sub_handler = getattr(handler, method)
        if not hasattr(sub_handler, "__schemas__"):
            return await handler(request)
        schemas = sub_handler.__schemas__
    else:
        schemas = handler.__schemas__
    kwargs = {}
    for schema in schemas:
        try:
            data = await parser.parse(
                schema["schema"], request, locations=schema["locations"]
            )
        except web.HTTPClientError as error:
            return (error_handler or _default_error_handler)(error)
        if data:
            kwargs.update(data)
    kwargs.update(request.match_info)
    # request.data will be removed since 1.0.0
    request[request.app["_apispec_request_data_name"]] = request.data = kwargs
    return await handler(request)


def _default_error_handler(error_handler):
    """
    Use it to customize error handler.
    In aiohttp-apispec we use 400 as default client http error code.
    """
    error_handler.set_status(400)
    return error_handler
