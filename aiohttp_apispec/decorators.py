from apispec.ext.marshmallow.swagger import schema2parameters


def docs(**kwargs):
    def wrapper(func):
        kwargs['produces'] = ['application/json']
        if not hasattr(func, '__apispec__'):
            func.__apispec__ = {'parameters': [], 'responses': {}, 'docked': {}}
        func.__apispec__.update(kwargs)
        func.__apispec__['docked'] = {'route': False}
        return func
    return wrapper


def use_kwargs(schema, **kwargs):
    if callable(schema):
        schema = schema()
    # location kwarg added for compatibility with old versions
    locations = kwargs.get('locations', [])
    if not locations:
        locations = kwargs.get('location')
        if locations:
            locations = [locations]
        else:
            locations = None

    options = {'required': kwargs.get('required', False)}
    if locations:
        options['default_in'] = locations[0]

    def wrapper(func):
        parameters = schema2parameters(schema, **options)
        if not hasattr(func, '__apispec__'):
            func.__apispec__ = {'parameters': [], 'responses': {}, 'docked': {}}
        func.__apispec__['parameters'].extend(parameters)
        if not hasattr(func, '__schemas__'):
            func.__schemas__ = []
        func.__schemas__.append({'schema': schema,
                                 'locations': locations})

        return func
    return wrapper


def marshal_with(schema, code=200, required=False):
    if callable(schema):
        schema = schema()

    def wrapper(func):
        if not hasattr(func, '__apispec__'):
            func.__apispec__ = {'parameters': [], 'responses': {}, 'docked': {}}
        func.__apispec__['responses']['%s' % code] = schema2parameters(schema, required=required)[0]
        return func

    return wrapper
