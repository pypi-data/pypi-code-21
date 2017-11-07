"""Exposes the StdOut recorder."""
from __future__ import print_function


class StdOut(object):
    """Print results to stdout.

    Args:
        values (dict): key-value pairs to be printed
    """

    def __init__(self, values):
        """Initialize the recorder."""
        self.values = values

    def write(self, results):
        """Print the results to stdout."""
        for field in self.values:
            print('{0}: {1}'.format(field, self.values[field](results)))
