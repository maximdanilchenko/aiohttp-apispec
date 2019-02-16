<h1 align="center">aiohttp-apispec</h1>
<p align="center">Build and document REST APIs with <a href="https://github.com/aio-libs/aiohttp">aiohttp</a> and <a href="https://github.com/marshmallow-code/apispec">apispec</a></p>

<p align="center">
  <a href="https://pypi.python.org/pypi/aiohttp-apispec"><img src="https://badge.fury.io/py/aiohttp-apispec.svg" alt="Pypi"></a>
  <a href="https://travis-ci.org/maximdanilchenko/aiohttp-apispec"><img src="https://travis-ci.org/maximdanilchenko/aiohttp-apispec.svg" alt="build status"></a>
  <a href="https://codecov.io/gh/maximdanilchenko/aiohttp-apispec"><img src="https://codecov.io/gh/maximdanilchenko/aiohttp-apispec/branch/master/graph/badge.svg" alt="[codcov]"></a>
</p>
<p align="center">
  <a href="https://aiohttp-apispec.readthedocs.io/en/latest/?badge=latest"><img src="https://readthedocs.org/projects/aiohttp-apispec/badge/?version=latest" alt="[docs]"></a>
  <a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
  <a href="https://github.com/maximdanilchenko/aiohttp-apispec/graphs/contributors"><img src="https://img.shields.io/github/contributors/maximdanilchenko/aiohttp-apispec.svg" alt="Contributors"></a>
</p>
<p align="center">
   <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.5-blue.svg" alt="Python 3.5"></a>
   <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.6-blue.svg" alt="Python 3.6"></a>
   <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.7-blue.svg" alt="Python 3.7"></a>
</p>


![img](https://user-images.githubusercontent.com/10708076/40740929-bd141942-6452-11e8-911c-d9032f8d625f.png)

<p>

```aiohttp-apispec``` key features:
- ```docs```, ```request_schema``` and ```response_schema``` decorators 
to add swagger spec support out of the box. *If you have < 1.0.0 version you should use 
```use_kwags``` and ```marshal_with``` decorators 
instead of ```request_schema``` and ```response_schema``` respectively.*
- ```validation_middleware``` middleware to enable validating 
with marshmallow schemas from those decorators

```aiohttp-apispec``` api is fully inspired by ```flask-apispec``` library

## Contents

- [Install](#install)
- [Quickstart](#quickstart)
- [Adding validation middleware](#adding-validation-middleware)
- [Build swagger web client](#build-swagger-web-client)


## Install

```
pip install aiohttp-apispec
```

## Quickstart

```Python
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
    setup_aiohttp_apispec,
)
from aiohttp import web
from marshmallow import Schema, fields


class RequestSchema(Schema):
    id = fields.Int()
    name = fields.Str(description="name")


class ResponseSchema(Schema):
    msg = fields.Str()
    data = fields.Dict()


@docs(
    tags=["mytag"],
    summary="Test method summary",
    description="Test method description",
)
@request_schema(RequestSchema(strict=True))
@response_schema(ResponseSchema(), 200)
async def index(request):
    return web.json_response({"msg": "done", "data": {}})


app = web.Application()
app.router.add_post("/v1/test", index)

# init docs with all parameters, usual for ApiSpec
setup_aiohttp_apispec(app=app, title="My Documentation", version="v1")

# now we can find it on 'http://localhost:8080/api/docs/api-docs'
web.run_app(app)
```
Class based views are also supported:
```python
class TheView(web.View):
    @docs(
        tags=["mytag"],
        summary="View method summary",
        description="View method description",
    )
    @request_schema(RequestSchema(strict=True))
    @response_schema(ResponseSchema(), 200)
    def delete(self):
        return web.json_response(
            {"msg": "done", "data": {"name": self.request["data"]["name"]}}
        )


app.router.add_view("/v1/view", TheView)
```

As alternative you can add responses info to `docs` decorator, which is more compact way. 
And it allows you not to use schemas for responses documentation:

```python
@docs(
    tags=["mytag"],
    summary="Test method summary",
    description="Test method description",
    responses={
        200: {
            "schema": ResponseSchema(),
            "description": "Success response",
        },  # regular response
        404: {"description": "Not found"},  # responses without schema
        422: {"description": "Validation error"},
    },
)
@request_schema(RequestSchema(strict=True))
async def index(request):
    return web.json_response({"msg": "done", "data": {}})
```

## Adding validation middleware

```Python
from aiohttp_apispec import validation_middleware

...

app.middlewares.append(validation_middleware)
```
Now you can access all validated data in route from ```request['data']``` like so:

```Python
@docs(
    tags=["mytag"],
    summary="Test method summary",
    description="Test method description",
)
@request_schema(RequestSchema(strict=True))
@response_schema(ResponseSchema(), 200)
async def index(request):
    uid = request["data"]["id"]
    name = request["data"]["name"]
    return web.json_response(
        {"msg": "done", "data": {"info": f"name - {name}, id - {uid}"}}
    )
```


You can change ``Request``'s ``'data'`` param to another with ``request_data_name`` argument of 
``setup_aiohttp_apispec`` function:

```python
setup_aiohttp_apispec(
    app=app,
    request_data_name="validated_data",
    title="My Documentation",
    version="v1",
    url="/api/docs/api-docs",
)

...


@request_schema(RequestSchema(strict=True))
async def index(request):
    uid = request["validated_data"]["id"]
    ...
```

If you want to catch validation errors you should write your own middleware and catch 
```web.HTTPClientError```, ```json.JSONDecodeError``` and so on. Like this:
```python
@web.middleware
async def my_middleware(request, handler):
    try:
        return await handler(request)
    except web.HTTPClientError:
        return web.json_response(status=400)


app.middlewares.extend(
    [
        my_middleware,  # Catch exception by your own, format it and respond to client
        validation_middleware,
    ]
)

```

## Build swagger web client
`aiohttp-apispec` adds `swagger_dict` parameter to aiohttp web application after initialization (with `setup_aiohttp_apispec` function). 
So you can use it easily with [aiohttp_swagger](https://github.com/cr0hn/aiohttp-swagger) library:

```Python
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_swagger import setup_swagger


def create_app(app):
    setup_aiohttp_apispec(app)

    async def swagger(app):
        setup_swagger(
            app=app, swagger_url="/api/doc", swagger_info=app["swagger_dict"]
        )

    app.on_startup.append(swagger)
    # now we can access swagger client on '/api/doc' url
    ...
    return app
```
