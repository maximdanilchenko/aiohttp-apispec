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
        response_info = sub_handler.__apispec__["responses"]
    else:
        schemas = orig_handler.__schemas__
        response_info = orig_handler.__apispec__["responses"]
    result = {}
    for schema in schemas:
        data = await request.app["_apispec_parser"].parse(
            schema["schema"], request, locations=schema["locations"]
        )
        if schema["put_into"]:
            request[schema["put_into"]] = data
        elif data:
            try:
                result.update(data)
            except (ValueError, TypeError):
                result = data
                break
    request[request.app["_apispec_request_data_name"]] = result
    response = await handler(request)
    response_schema = response_info.get(str(response.status))
    if response_schema:
        response_schema["schema"].loads(response.text)
    return response
