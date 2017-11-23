"""Cloudsmith CLI Controller."""
from __future__ import absolute_import, print_function, unicode_literals
from cement.core.controller import CementBaseController, expose


class CloudsmithCliController(CementBaseController):
    """The Cloudsmith CLI Controller."""

    class Meta(object):  # noqa
        label = 'base'
        description = "Cloudsmith Command Line Interface (CLI)"
        arguments = [
            (['-f', '--foo'],
             dict(action='store', help='the notorious foo option')),
            (['-C'],
             dict(action='store_true', help='the big C option')),
        ]

    @expose(hide=True)
    def default(self):
        self.app.log.info('Inside MyBaseController.default()')
        if self.app.pargs.foo:
            print("Recieved option: foo => %s" % self.app.pargs.foo)

    @expose(help="this command does relatively nothing useful")
    def command1(self):
        self.app.log.info("Inside MyBaseController.command1()")
