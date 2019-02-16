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

``aiohttp-apispec`` key features:

- ``docs``, ``request_schema`` and ``response_schema`` decorators to add swagger spec support out of the box. If you have < 1.0.0 version you should use ``use_kwags`` and ``marshal_with`` decorators instead of ``request_schema`` and ``response_schema`` respectively.

- ``validation_middleware`` middleware to enable validating with marshmallow schemas from those decorators

``aiohttp-apispec`` api is fully inspired by ``flask-apispec`` library

Guide
-----

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    usage
    install
    api
