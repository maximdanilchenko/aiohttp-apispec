def docs(**kwargs):
    """
    Annotate the decorated view function with the specified Swagger
    attributes.

    Usage:

    .. code-block:: python

        from aiohttp import web

        @docs(tags=['my_tag'],
              summary='Test method summary',
              description='Test method description',
              parameters=[{
                      'in': 'header',
                      'name': 'X-Request-ID',
                      'schema': {'type': 'string', 'format': 'uuid'},
                      'required': 'true'
                  }]
              )
        async def index(request):
            return web.json_response({'msg': 'done', 'data': {}})

    """

    def wrapper(func):
        if not kwargs.get("produces"):
            kwargs["produces"] = ["application/json"]
        if not hasattr(func, "__apispec__"):
            func.__apispec__ = {"parameters": [], "responses": {}}
        extra_parameters = kwargs.pop("parameters", [])
        extra_responses = kwargs.pop("responses", {})
        func.__apispec__["parameters"].extend(extra_parameters)
        func.__apispec__["responses"].update(extra_responses)
        func.__apispec__.update(kwargs)
        if not hasattr(func, "__schemas__"):
            func.__schemas__ = []
        return func

    return wrapper


def request_schema(schema, locations=None, **kwargs):
    """
    Add request info into the swagger spec and
    prepare injection keyword arguments from the specified
    webargs arguments into the decorated view function in
    request['data'] for validation_middleware validation middleware.

    Usage:

    .. code-block:: python

        from aiohttp import web
        from marshmallow import Schema, fields


        class RequestSchema(Schema):
            id = fields.Int()
            name = fields.Str(description='name')

        @request_schema(RequestSchema(strict=True))
        async def index(request):
            # aiohttp_apispec_middleware should be used for it
            data = request['data']
            return web.json_response({'name': data['name'],
                                      'id': data['id']})

    :param schema: :class:`Schema <marshmallow.Schema>` class or instance
    :param locations: Default request locations to parse
    """
    if callable(schema):
        schema = schema()
    # location kwarg added for compatibility with old versions
    locations = locations or []
    if not locations:
        locations = kwargs.get("location")
        if locations:
            locations = [locations]
        else:
            locations = None

    options = {"required": kwargs.get("required", False)}
    if locations:
        options["default_in"] = locations[0]

    def wrapper(func):
        if not hasattr(func, "__apispec__"):
            func.__apispec__ = {"parameters": [], "responses": {}}
        func.__apispec__["options"] = options
        func.__apispec__["schema"] = schema
        if not hasattr(func, "__schemas__"):
            func.__schemas__ = []
        if locations and "body" in locations:
            body_schema_exists = (
                "body" in func_schema["locations"] for func_schema in func.__schemas__
            )
            if any(body_schema_exists):
                raise RuntimeError("Multiple body parameters are not allowed")
        func.__schemas__.append({"schema": schema, "locations": locations})

        return func

    return wrapper


use_kwargs = request_schema


def response_schema(schema, code=200, required=False, description=None):
    """
    Add response info into the swagger spec

    Usage:

    .. code-block:: python

        from aiohttp import web
        from marshmallow import Schema, fields


        class ResponseSchema(Schema):
            msg = fields.Str()
            data = fields.Dict()

        @response_schema(ResponseSchema(), 200)
        async def index(request):
            return web.json_response({'msg': 'done', 'data': {}})

    :param str description: response description
    :param bool required:
    :param schema: :class:`Schema <marshmallow.Schema>` class or instance
    :param int code: HTTP response code
    """
    if callable(schema):
        schema = schema()

    def wrapper(func):
        if not hasattr(func, "__apispec__"):
            func.__apispec__ = {"parameters": [], "responses": {}}
        func.__apispec__["responses"]["%s" % code] = {
            "schema": schema,
            "required": required,
            "description": description,
        }
        return func

    return wrapper


marshal_with = response_schema
