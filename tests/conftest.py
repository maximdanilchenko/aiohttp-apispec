import pytest
from marshmallow import Schema, fields

from aiohttp_apispec import AiohttpApiSpec


def pytest_report_header(config):
    return """
          .   .  .                                   
,-. . ,-. |-. |- |- ,-.    ,-. ,-. . ,-. ,-. ,-. ,-. 
,-| | | | | | |  |  | | -- ,-| | | | `-. | | |-' |   
`-^ ' `-' ' ' `' `' |-'    `-^ |-' ' `-' |-' `-' `-' 
                    |          |         |           
                    '          '         '           
    """


@pytest.fixture
def doc():
    return AiohttpApiSpec(
        title='My Documentation', version='v1', url='/api/docs/api-docs'
    )


@pytest.fixture
def request_schema():
    class RequestSchema(Schema):
        id = fields.Int()
        name = fields.Str(description='name')
        bool_field = fields.Bool()
        list_field = fields.List(fields.Int())

    return RequestSchema(strict=True)


@pytest.fixture
def request_callable_schema():
    class RequestSchema(Schema):
        id = fields.Int()
        name = fields.Str(description='name')
        bool_field = fields.Bool()
        list_field = fields.List(fields.Int())

    return RequestSchema


@pytest.fixture
def response_schema():
    class ResponseSchema(Schema):
        msg = fields.Str()
        data = fields.Dict()

    return ResponseSchema()
