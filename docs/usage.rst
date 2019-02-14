.. _usage:

Usage
=====

Quickstart
----------

.. code-block:: python

    from aiohttp_apispec import (docs,
                                 request_schema,
                                 response_schema,
                                 setup_aiohttp_apispec)
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
          summary='Test method summary',
          description='Test method description')
    @request_schema(RequestSchema(strict=True))
    @response_schema(ResponseSchema(), 200)
    async def index(request):
        return web.json_response({'msg': 'done',
                                  'data': {}})

    # Class based views are also supported:
    class TheView(web.View):
        @docs(
            tags=['mytag'],
            summary='View method summary',
            description='View method description',
        )
        @request_schema(RequestSchema(strict=True))
        def delete(self):
            return web.json_response({
                'msg': 'done',
                'data': {'name': self.request['data']['name']},
            })


    app = web.Application()
    app.router.add_post('/v1/test', index)
    app.router.add_view('/v1/view', TheView)

    # init docs with all parameters, usual for ApiSpec
    setup_aiohttp_apispec(app=app, title="My Documentation", version="v1")


    # find it on 'http://localhost:8080/api/docs/api-docs'
    web.run_app(app)

Adding validation middleware
----------------------------

.. code-block:: python

    from aiohttp_apispec import validation_middleware

    ...

    app.middlewares.append(validation_middleware)

Now you can access all validated data in route from ``request['data']`` like so:

.. code-block:: python

    @docs(tags=['mytag'],
          summary='Test method summary',
          description='Test method description')
    @request_schema(RequestSchema(strict=True))
    @response_schema(ResponseSchema(), 200)
    async def index(request):
        uid = request['data']['id']
        name = request['data']['name']
        return web.json_response(
            {'msg': 'done',
             'data': {'info': f'name - {name}, id - {uid}'}}
         )

You can change ``Request``'s ``'data'`` param to another
with ``request_data_name`` argument of ``setup_aiohttp_apispec`` function:

.. code-block:: python

    setup_aiohttp_apispec(app=app,
                          request_data_name='validated_data',
                          title='My Documentation',
                          version='v1',
                          url='/api/docs/api-docs')

    ...

    @request_schema(RequestSchema(strict=True))
    async def index(request):
        uid = request['validated_data']['id']
        ...

If you want to catch validation errors you should write your own middleware and catch
``web.HTTPClientError``, ``json.JSONDecodeError`` and so on. Like this:

.. code-block:: python

    @web.middleware
    async def my_middleware(request, handler):
        try:
            return await handler(request)
        except web.HTTPClientError:
            return web.json_response(status=400)

    app.middlewares.extend([
        my_middleware,  # Catch exception by your own, format it and respond to client
        validation_middleware,
    ])

Build swagger web client
------------------------

``aiohttp-apispec`` adds ``swagger_dict`` parameter to aiohttp
web application after initialization (with ``setup_aiohttp_apispec`` function).
So you can use it easily with ``aiohttp_swagger`` library:

.. code-block:: python

    from aiohttp_apispec import setup_aiohttp_apispec
    from aiohttp_swagger import setup_swagger


    def create_app(app):
        setup_aiohttp_apispec(app)

        async def swagger(app):
            setup_swagger(
                app=app, swagger_url='/api/doc', swagger_info=app['swagger_dict']
            )
        app.on_startup.append(swagger)
        # now we can access swagger client on '/api/doc' url
        ...
        return app

Now we can access swagger client on ``/api/doc`` url
