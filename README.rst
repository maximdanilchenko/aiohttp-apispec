*******
aoihttp-apispec
*******

Build and document REST APIs with aiohttp and apispec

Quickstart
----------

.. code-block:: python


    from aiohttp_apispec import docs, use_kwargs, marshal_with, AiohttpApiSpec
    from aiohttp import web
    from marshmallow import Schema, fields


    class RequestSchema(Schema):
        id = fields.Int()
        name = fields.Str(description='name')
        bool_field = fields.Bool()


    class ResponseSchema(Schema):
        msg = fields.Str()
        data = fields.Dict()


    @docs(tags=['mytag'],
          summary=u'Test method summary',
          description=u'Test method description')
    @use_kwargs(RequestSchema())
    @marshal_with(ResponseSchema(), 200)
    async def index(request, **data):
        return web.json_response({'msg': 'done', 'data': {}})


    app = web.Application()
    app.router.add_post('/v1/test', index)

    # init docs with all parameters, usual for ApiSpec
    docs = AiohttpApiSpec(title='My Documentation',
                          version='v1',
                          url='/api/docs/api-docs')

    # add startup method to form swagger json
    app.on_startup.append(docs.register)

    # now we can find it on 'http://localhost:8080/api/docs/api-docs'
    web.run_app(app)


