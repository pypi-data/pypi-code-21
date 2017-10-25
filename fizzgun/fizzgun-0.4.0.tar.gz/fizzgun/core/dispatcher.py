from fizzgun.core.common import Worker


class Dispatcher(Worker):
    """
    Generic component. Acts as a load balancer
    """

    def process(self, work):
        yield work
