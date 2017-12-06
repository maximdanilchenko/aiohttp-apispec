import json
import asyncio

from aiohttp import web


@web.middleware
@asyncio.coroutine
def aoihttp_apispec_middleware(request: web.Request,
                               handler,
                               json_worker=json,
                               error_handler=None) -> web.Response:
    if not hasattr(handler, '__schemas__'):
        return (yield from handler(request))
    kwargs = {}
    for schema in handler.__schemas__:
        if schema['location'] == 'body':
            request_data = yield from request.json(loads=json_worker.loads)
        else:
            request_data = request.query
        data, errors = schema['schema'].load(data=request_data)
        if errors:
            return (error_handler or _default_error_handler)(errors)
        kwargs.update(data)
    kwargs.update(request.match_info)
    request.data = kwargs
    return (yield from handler(request))


def _default_error_handler(errors):
    return web.Response(body=json.dumps(errors), status=400)
