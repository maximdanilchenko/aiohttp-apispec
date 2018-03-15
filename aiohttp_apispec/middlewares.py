import asyncio
from webargs.aiohttpparser import parser

from aiohttp import web


@web.middleware
@asyncio.coroutine
def aiohttp_apispec_middleware(request: web.Request,
                               handler,
                               error_handler=None) -> web.Response:
    if not hasattr(handler, '__schemas__'):
        return (yield from handler(request))
    kwargs = {}
    for schema in handler.__schemas__:
        try:
            data = (yield from parser.parse(schema['schema'],
                                            request,
                                            locations=schema['locations']))
        except web.HTTPClientError as error:
            return (error_handler or _default_error_handler)(error)
        if data:
            kwargs.update(data)
    kwargs.update(request.match_info)
    request.data = kwargs
    return (yield from handler(request))


def _default_error_handler(error_handler):
    """
    Use it to customize error handler.
    In aiohttp-apispec we use 400 as default client http error code.
    """
    error_handler.set_status(400)
    return error_handler
