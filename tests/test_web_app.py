
async def test_response_200_get(aiohttp_app):
    res = await aiohttp_app.get('/v1/test', params={'id': 1, 'name': 'max'})
    assert res.status == 200


async def test_response_422_get(aiohttp_app):
    res = await aiohttp_app.get(
        '/v1/test', params={'id': 'string', 'name': 'max'}
    )
    assert res.status == 422


async def test_response_200_post(aiohttp_app):
    res = await aiohttp_app.post('/v1/test', json={'id': 1, 'name': 'max'})
    assert res.status == 200


async def test_response_200_post_callable_schema(aiohttp_app):
    res = await aiohttp_app.post(
        '/v1/test_call', json={'id': 1, 'name': 'max'}
    )
    assert res.status == 200


async def test_response_422_post(aiohttp_app):
    res = await aiohttp_app.post(
        '/v1/test', json={'id': 'string', 'name': 'max'}
    )
    assert res.status == 422


async def test_response_not_docked(aiohttp_app):
    res = await aiohttp_app.get('/v1/other', params={'id': 1, 'name': 'max'})
    assert res.status == 200


async def test_response_data_post(aiohttp_app):
    res = await aiohttp_app.post(
        '/v1/echo', json={'id': 1, 'name': 'max', 'list_field': [1, 2, 3, 4]}
    )
    assert (await res.json()) == {
        'id': 1,
        'name': 'max',
        'list_field': [1, 2, 3, 4],
    }


async def test_response_data_get_old_data(aiohttp_app):
    res = await aiohttp_app.get(
        '/v1/echo_old',
        params=[
            ('id', '1'),
            ('name', 'max'),
            ('bool_field', '0'),
            ('list_field', '1'),
            ('list_field', '2'),
            ('list_field', '3'),
            ('list_field', '4'),
        ],
    )
    assert (await res.json()) == {
        'id': 1,
        'name': 'max',
        'bool_field': False,
        'list_field': [1, 2, 3, 4],
    }


async def test_response_data_get(aiohttp_app):
    res = await aiohttp_app.get(
        '/v1/echo',
        params=[
            ('id', '1'),
            ('name', 'max'),
            ('bool_field', '0'),
            ('list_field', '1'),
            ('list_field', '2'),
            ('list_field', '3'),
            ('list_field', '4'),
        ],
    )
    assert (await res.json()) == {
        'id': 1,
        'name': 'max',
        'bool_field': False,
        'list_field': [1, 2, 3, 4],
    }


async def test_response_data_class_get(aiohttp_app):
    res = await aiohttp_app.get(
        '/v1/class_echo',
        params=[
            ('id', '1'),
            ('name', 'max'),
            ('bool_field', '0'),
            ('list_field', '1'),
            ('list_field', '2'),
            ('list_field', '3'),
            ('list_field', '4'),
        ],
    )
    assert (await res.json()) == {
        'id': 1,
        'name': 'max',
        'bool_field': False,
        'list_field': [1, 2, 3, 4],
    }


async def test_response_data_class_post(aiohttp_app):
    res = await aiohttp_app.post('/v1/class_echo')
    assert res.status == 405


async def test_response_data_class_without_spec(aiohttp_app):
    res = await aiohttp_app.delete('/v1/class_echo')
    assert (await res.json()) == {'hello': 'world'}


async def test_swagger_handler_200(aiohttp_app):
    res = await aiohttp_app.get('/v1/api/docs/api-docs')
    assert res.status == 200
