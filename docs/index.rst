===============
apispec-aiohttp
===============

.. image:: https://badge.fury.io/py/apispec-aiohttp.svg
    :target: https://pypi.python.org/pypi/apispec-aiohttp

.. image:: https://travis-ci.org/kulapard/apispec-aiohttp.svg
    :target: https://travis-ci.org/kulapard/apispec-aiohttp

.. image:: https://codecov.io/gh/kulapard/apispec-aiohttp/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/kulapard/apispec-aiohttp

Build and document REST APIs with aiohttp and apispec

``apispec-aiohttp`` key features:

- ``docs``, ``request_schema``, ``match_info_schema``, ``querystring_schema``, ``form_schema``, ``json_schema``, ``headers_schema``, ``cookies_schema``, decorators to add swagger spec support out of the box;

- ``validation_middleware`` middleware to enable validating with marshmallow schemas from those decorators;

- **SwaggerUI** support.

``apispec-aiohttp`` api is fully inspired by ``flask-apispec`` library

Guide
-----

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    usage
    install
    api
