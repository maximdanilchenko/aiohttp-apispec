<h1 align="center">aiohttp-apispec</h1>

<p align="center">
  <a href="https://pypi.python.org/pypi/aiohttp-apispec"><img src="https://badge.fury.io/py/aiohttp-apispec.svg" alt="Pypi"></a>
  <a href="https://travis-ci.org/maximdanilchenko/aiohttp-apispec"><img src="https://travis-ci.org/maximdanilchenko/aiohttp-apispec.svg" alt="build status"></a>
  <a href="https://codecov.io/gh/maximdanilchenko/aiohttp-apispec"><img src="https://codecov.io/gh/maximdanilchenko/aiohttp-apispec/branch/master/graph/badge.svg" alt="[codcov]"></a>
  <a href="https://aiohttp-apispec.readthedocs.io/en/latest/?badge=latest"><img src="https://readthedocs.org/projects/aiohttp-apispec/badge/?version=latest" alt="[docs]"></a>
  <a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
</p>

<p align="center">Build and document REST APIs with <a href="https://github.com/aio-libs/aiohttp">aiohttp</a> and <a href="https://github.com/marshmallow-code/apispec">apispec</a></p>


![img](https://user-images.githubusercontent.com/10708076/40740929-bd141942-6452-11e8-911c-d9032f8d625f.png)

<p>

```aiohttp-apispec``` key features:
- ```docs```, ```use_kwargs``` and ```marshal_with``` decorators 
to add swagger spec support out of the box
- ```aiohttp_apispec_middleware``` middleware to enable validating 
with marshmallow schemas from those decorators

```aiohttp-apispec``` api is fully inspired by ```flask-apispec``` library

## Install

```
pip install aiohttp-apispec
```

## Quickstart

```Python
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


@docs(
    tags=['mytag'],
    summary='Test method summary',
    description='Test method description',
)
@use_kwargs(RequestSchema(strict=True))
@marshal_with(ResponseSchema(), 200)
async def index(request):
    return web.json_response({'msg': 'done', 'data': {}})


app = web.Application()
app.router.add_post('/v1/test', index)

# init docs with all parameters, usual for ApiSpec
doc = AiohttpApiSpec(
    app=app, title='My Documentation', version='v1', url='/api/docs/api-docs'
)

# now we can find it on 'http://localhost:8080/api/docs/api-docs'
web.run_app(app)
```
## Adding validation middleware

```Python
from aiohttp_apispec import aiohttp_apispec_middleware

...

app.middlewares.append(aiohttp_apispec_middleware)
```
Now you can access all validated data in route from ```request['data']``` like so:

```Python
@docs(
    tags=['mytag'],
    summary='Test method summary',
    description='Test method description',
)
@use_kwargs(RequestSchema(strict=True))
@marshal_with(ResponseSchema(), 200)
async def index(request):
    uid = request['data']['id']
    name = request['data']['name']
    return web.json_response(
        {'msg': 'done', 'data': {'info': f'name - {name}, id - {uid}'}}
    )
```

## Build swagger web client
```aiohttp-apispec``` adds ```swagger_dict``` parameter to aiohttp web application after initialization. 
So you can use it easily with [aiohttp_swagger](https://github.com/cr0hn/aiohttp-swagger) library:

```Python
from aiohttp_swagger import setup_swagger

...

async def swagger(app):
    setup_swagger(
        app=app, swagger_url='/api/doc', swagger_info=app['swagger_dict']
    )
app.on_startup.append(swagger)
# now we can access swagger client on /api/doc url
```

<p>

## TODO List before 1.0.0 can be released:

- [x] Generating json spec from marshmallow data schemas
- [x] Kwargs/marshal_with decorators for request/response schemas and docs decorator for connecting schemas to swagger spec with additional params through aiohttp routes
- [x] Data validation through additional middleware (built using [webargs](https://github.com/sloria/webargs))
- [x] 97% more cov with tests
- [x] Documentation on [readthedocs](http://aiohttp-apispec.readthedocs.io/en/latest/)
- [x] More simple initialisation - register method is not needed. Instead of it we can use some middleware to register all routs on app start
- [ ] Flexible settings for  ```aiohttp_apispec_middleware``` middleware
- [ ] Nested apps support
- [ ] More complex settings (like request param name)
