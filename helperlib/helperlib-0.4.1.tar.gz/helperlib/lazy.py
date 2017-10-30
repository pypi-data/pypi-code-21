class LazyProxy(object):
    def __init__(self, cls, args=None, kwargs=None):
        self.inst = None
        self.args = args or []
        self.kwargs = kwargs or {}

    def __getattr__(self, name):
        if not self.inst:
            sef.inst = cls(*self.args, **self.kwargs)
        return getattr(self.inst, name)
