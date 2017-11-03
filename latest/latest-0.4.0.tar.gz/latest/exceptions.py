""":mod:`exceptions` module contains exceptions classes defined for :mod:`latest` package.

"""


class LatestError(Exception):
    """Base class for all :mod:`latest` exceptions."""

    def __init__(self, details):
        self.details = details

    def __str__(self):
        return self.__class__.__name__ + ":\n\t" + self.details


class PyExprSyntaxError(LatestError):
    """Exception raised when bad syntax code is parsed in a template."""

    def __init__(self, details):
        super(self.__class__, self).__init__(details)
        self.report = "Problems occurred trying to match the template with the context."


class ContextError(LatestError):
    """Exception raised when context dictionary doesn't match names required by a template."""

    def __init__(self, details):
        super(self.__class__, self).__init__(details)
        self.report = "Problems occurred trying to parse the template."

