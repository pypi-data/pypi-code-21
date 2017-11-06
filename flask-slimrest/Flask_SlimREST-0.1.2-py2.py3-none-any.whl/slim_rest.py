import re


def _convert_camel_case_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class SlimRest:
    def __init__(self, app=None):
        self._lazy_queue = []
        self._app = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self._app = app
        for path, function, methods, prefix in self._lazy_queue:
            self._register_endpoint(path, function, methods, prefix)

    def _lazy_register_endpoint(self, path, function, methods, prefix):
        if self._app:
            self._register_endpoint(path, function, methods, prefix)
        else:
            self._lazy_queue.append((path, function, methods, prefix))

    def _register_endpoint(self, path, function, methods, prefix):
        self._app.add_url_rule(
            path,
            endpoint=prefix + "_" + function.__name__,
            view_func=function,
            methods=methods
        )

    def add_namespace(self, path, namespace_endpoint_prefix=None):
        def wrapper(cls):
            instance = cls()
            prefix = namespace_endpoint_prefix
            if not prefix:
                prefix = _convert_camel_case_to_underscore(cls.__name__)
            for name, function in cls.__dict__.items():
                if hasattr(function, '__endpoint'):
                    metadata = getattr(function, '__endpoint')
                    self._lazy_register_endpoint(
                        path + metadata['path'],
                        getattr(instance, name),
                        metadata['methods'],
                        prefix
                    )
            return cls
        return wrapper

