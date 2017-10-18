"""The base command."""


class Base(object):
    """A base command."""

    def __init__(self, utils, options, *args, **kwargs):

#    def __init__(self, options, *args, **kwargs):
        self.utils = utils
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')
