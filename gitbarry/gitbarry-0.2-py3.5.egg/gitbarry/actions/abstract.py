class AbstractAction(object):
    def __init__(self, params):
        self.params = params
        self.init()

    def init(self):
        pass

    def run(self):
        raise NotImplementedError("You must implement this method")

