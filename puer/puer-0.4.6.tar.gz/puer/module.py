class AbstractModule(object):
    name = "abstract"
    value = None

    def __init__(self, manager, app):
        self.value = None
