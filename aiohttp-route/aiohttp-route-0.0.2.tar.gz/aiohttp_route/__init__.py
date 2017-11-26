import sys
from functools import wraps
from types import ModuleType


def route(method, endpoint, name=None, newstyle=False):
    def decorator(handler):
        handler.__aiohttp_route__ = True
        handler.route_descriptor = {
            'method': method,
            'path': endpoint
        }
        if name is not None:
            handler.route_descriptor['name'] = name

        @wraps(handler)
        async def decorated(*args, **kwargs):
            return (await handler(*args, **kwargs, **args[0].match_info))

        if newstyle:
            return decorated
        else:
            return handler
    return decorator


def router(app, modules):
    for index, module in enumerate(modules):
        if isinstance(module, str):
            modules[index] = __import__(module)
        elif isinstance(module, ModuleType):
            pass
        else:
            raise RuntimeError(
                'Expected string or module got {}'.format(
                    type(module)
                ))
    return [
        app.router.add_route(handler=handler, **handler.route_descriptor)
        for module in modules
        for handler in [getattr(module, handler) for handler in dir(module)]
        if hasattr(handler, '__aiohttp_route__')
    ]
