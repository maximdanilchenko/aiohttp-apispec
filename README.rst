===============
aiohttp-apispec
===============

.. image:: https://badge.fury.io/py/aiohttp-apispec.svg
    :target: https://pypi.python.org/pypi/aiohttp-apispec
.. image:: https://travis-ci.org/maximdanilchenko/aiohttp-apispec.svg
    :target: https://travis-ci.org/maximdanilchenko/aiohttp-apispec
.. image:: https://codecov.io/gh/maximdanilchenko/aiohttp-apispec/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/maximdanilchenko/aiohttp-apispec

Build and document REST APIs with aiohttp and apispec

Install
-------

::

    pip install aiohttp-apispec

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
          summary='Test method summary',
          description='Test method description')
    @use_kwargs(RequestSchema(strict=True))
    @marshal_with(ResponseSchema(), 200)
    async def index(request):
        return web.json_response({'msg': 'done', 'data': {}})


    app = web.Application()
    app.router.add_post('/v1/test', index)

    # init docs with all parameters, usual for ApiSpec
    doc = AiohttpApiSpec(title='My Documentation',
                         version='v1',
                         url='/api/docs/api-docs')

    # add method to form swagger json:
    doc.register(app)  # we should do it only after all routes are added to router!

    # now we can find it on 'http://localhost:8080/api/docs/api-docs'
    web.run_app(app)

Adding validation middleware
----------------------------

.. code-block:: python


    from aiohttp_apispec import aiohttp_apispec_middleware

    ...

    app.middlewares.append(aiohttp_apispec_middleware)
    # now you can access all validated data in route from request['data']


Build swagger client with aiohttp_swagger library
-------------------------------------------------

.. code-block:: python

    from aiohttp_swagger import setup_swagger

    ...

    doc.register(app)
    setup_swagger(app=app, swagger_url='/api/doc', swagger_info=app['swagger_dict'])
    # now we can access swagger client on /api/doc url
