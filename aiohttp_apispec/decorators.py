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


def use_kwargs(schema, location=None, required=False):
    location = location or 'body'

    def wrapper(func):
        parameters = schema2parameters(schema, default_in=location, required=required)
        # print(parameters)
        if not hasattr(func, '__apispec__'):
            func.__apispec__ = {'parameters': [], 'responses': {}, 'docked': {}}
        func.__apispec__['parameters'].extend(parameters)
        if not hasattr(func, '__schemas__'):
            func.__schemas__ = []
        func.__schemas__.append({'schema': schema, 'location': location})

        return func
    return wrapper


def marshal_with(schema, code=200, required=False):

    def wrapper(func):
        if not hasattr(func, '__apispec__'):
            func.__apispec__ = {'parameters': [], 'responses': {}, 'docked': {}}
        func.__apispec__['responses']['%s' % code] = schema2parameters(schema, required=required)[0]
        return func

    return wrapper
