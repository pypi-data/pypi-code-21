"""Cloudsmith CLI Application."""
from __future__ import absolute_import, print_function, unicode_literals
from cement.core.foundation import CementApp
from . import controller


class CloudsmithCliApp(CementApp):
    """The Cloudsmith CLI Application."""

    class Meta(object):  # noqa
        label = 'cloudsmith-cli'
        handlers = [controller.CloudsmithCliController]
