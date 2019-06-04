from aiohttp import web

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
        data = await request.app["_apispec_parser"].parse(
            schema["schema"], request, locations=schema["locations"]
        )
        if data:
            if issubclass_py37fix(data, dict):
                kwargs.update(data)
            elif kwargs == {}:
                kwargs = data
            else:
                raise NotImplementedError
    if issubclass_py37fix(data, dict):
        kwargs.update(request.match_info)
    request[request.app["_apispec_request_data_name"]] = kwargs
    return await handler(request)
