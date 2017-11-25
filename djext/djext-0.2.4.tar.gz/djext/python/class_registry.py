class Registry(object):
    def __init__(self, klass):
        if type(klass) != 'type':
            raise ValueError('This decorator is intended for class decorating only')
        self.klass = klass
        self._subclass_registry = set()

    def _find_subclasses(self, klass):
        for subclass in klass.__subclasses__():
            if subclass not in self._subclass_registry:
                self._subclass_registry.add(subclass)
                self._find_subclasses(subclass)

    def _get_registry(self):
        if not self._subclass_registry:
            pass
        return self._subclass_registry

    def attach_registry(self):
        self._subclass_registry = set()
        pass

    def __call__(self, *args, **kwargs):
        return self.klass(*args, **kwargs)
