import pytest
from marshmallow import Schema, fields


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
