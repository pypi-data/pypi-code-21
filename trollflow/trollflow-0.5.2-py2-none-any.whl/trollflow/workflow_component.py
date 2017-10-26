import abc


class AbstractWorkflowComponent(object):
    __metaclass__ = abc.ABCMeta

    # @abc.abstractproperty
    slots = []

    def __init__(self):
        self.use_lock = False

    @abc.abstractmethod
    def pre_invoke(self):
        """Execute block before invoking component."""
        return

    @abc.abstractmethod
    def invoke(self, context):
        """Execute the actual component."""
        return

    @abc.abstractmethod
    def post_invoke(self):
        """Execute block after invoking component."""
        return
