# aiohttp-apispec

[![pypi](https://badge.fury.io/py/aiohttp-apispec.svg)](https://pypi.python.org/pypi/aiohttp-apispec)
[![build status](https://travis-ci.org/maximdanilchenko/aiohttp-apispec.svg)](https://travis-ci.org/maximdanilchenko/aiohttp-apispec)
[![codcov](https://codecov.io/gh/maximdanilchenko/aiohttp-apispec/branch/master/graph/badge.svg)](https://codecov.io/gh/maximdanilchenko/aiohttp-apispec)
[![docs](https://readthedocs.org/projects/aiohttp-apispec/badge/?version=latest)](https://aiohttp-apispec.readthedocs.io/en/latest/?badge=latest)

*Build and document REST APIs with [aiohttp](https://github.com/aio-libs/aiohttp) and [apispec](https://github.com/marshmallow-code/apispec)*

![img](https://user-images.githubusercontent.com/10708076/40740929-bd141942-6452-11e8-911c-d9032f8d625f.png)

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
```
## Adding validation middleware

```Python
from aiohttp_apispec import aiohttp_apispec_middleware

...

app.middlewares.append(aiohttp_apispec_middleware)
```
Now you can access all validated data in route from ```request['data']``` like so:

```Python
@docs(tags=['mytag'],
      summary='Test method summary',
      description='Test method description')
@use_kwargs(RequestSchema(strict=True))
@marshal_with(ResponseSchema(), 200)
async def index(request):
    uid = request['data']['id']
    name = request['data']['name']
    return web.json_response({'msg': 'done', 
                              'data': {'info': f'name - {name}, id - {uid}'}})
```

## Build swagger web client
You can do it easily with [aiohttp_swagger](https://github.com/cr0hn/aiohttp-swagger) library:

```Python
from aiohttp_swagger import setup_swagger

...

doc.register(app)
setup_swagger(app=app, swagger_url='/api/doc', swagger_info=app['swagger_dict'])
# now we can access swagger client on /api/doc url
```

TODO List before 1.0.0 can be released:

- [x] Generating json spec from marshmallow data schemas
- [x] Kwargs/marshal_with decorators for request/response schemas and docs decorator for connecting schemas to swagger spec with additional params through aiohttp routes
- [x] Data validation through additional middleware (built using [webargs](https://github.com/sloria/webargs))
- [x] 97% more cov with tests
- [x] Documentation on [readthedocs](http://aiohttp-apispec.readthedocs.io/en/latest/)
- [ ] More simple initialisation - register method is not needed. Instead of it we can use some middleware to register all routs on app start
- [ ] Nested apps support
- [ ] More complex settings (like request param name)
