import pytest
from marshmallow import Schema, fields

from aiohttp_apispec import AiohttpApiSpec

pytest_plugins = 'aiohttp.pytest_plugin'


@pytest.fixture
def doc():
    doc = AiohttpApiSpec(title='My Documentation',
                         version='v1',
                         url='/api/docs/api-docs')
    return doc


@pytest.fixture
def request_schema():
    class RequestSchema(Schema):
        id = fields.Int()
        name = fields.Str(description='name')
        bool_field = fields.Bool()
    return RequestSchema()


@pytest.fixture
def response_schema():
    class ResponseSchema(Schema):
        msg = fields.Str()
        data = fields.Dict()
    return ResponseSchema()
