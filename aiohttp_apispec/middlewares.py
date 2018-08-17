from aiohttp import web
from webargs.aiohttpparser import parser

from .utils import issubclass_py37fix


@web.middleware
async def aiohttp_apispec_middleware(
    request: web.Request, handler, error_handler=None
) -> web.Response:
    """
    Validation middleware for aiohttp web app

    Usage:

    .. code-block:: python

        app.middlewares.append(aiohttp_apispec_middleware)


    """
    if not hasattr(handler, '__schemas__'):
        if not issubclass_py37fix(handler, web.View):
            return await handler(request)
        method = request.method.lower()
        if not hasattr(handler, method):
            return await handler(request)
        sub_handler = getattr(handler, method)
        if not hasattr(sub_handler, '__schemas__'):
            return await handler(request)
        schemas = sub_handler.__schemas__
    else:
        schemas = handler.__schemas__
    kwargs = {}
    for schema in schemas:
        try:
            data = await parser.parse(
                schema['schema'], request, locations=schema['locations']
            )
        except web.HTTPClientError as error:
            return (error_handler or _default_error_handler)(error)
        if data:
            kwargs.update(data)
    kwargs.update(request.match_info)
    request['data'] = request.data = kwargs  # request.data will be removed since 1.0.0
    return await handler(request)


def _default_error_handler(error_handler):
    """
    Use it to customize error handler.
    In aiohttp-apispec we use 400 as default client http error code.
    """
    error_handler.set_status(400)
    return error_handler
