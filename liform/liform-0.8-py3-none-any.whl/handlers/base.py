class BaseRefreshHandler(object):
    def __init__(self, resource):
        self._resource = resource

    def try_sync(self, phase, settings, variables):
        return True

    def fore_phase(self, phase, settings, variables):
        pass

    def fore_children(self, phase, settings, variables):
        pass

    def post_children(self, phase, settings, variables):
        pass

    def post_phase(self, phase, settings, variables):
        pass


class BaseDestroyHandler(object):
    def __init__(self, resource):
        self._resource = resource

    def try_sync(self, phase, settings, variables):
        return True

    def fore_phase(self, phase, settings, variables):
        pass

    def fore_children(self, phase, settings, variables):
        pass

    def post_children(self, phase, settings, variables):
        pass

    def post_phase(self, phase, settings, variables):
        pass


class BaseHandler(object):
    def __init__(self, refresh, destroy, resource):
        self._resource = resource
        self.refresh = refresh(resource) if refresh else None
        self.destroy = destroy(resource) if destroy else None
