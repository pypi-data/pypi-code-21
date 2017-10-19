"""PyGTK Database Navigator command."""

# Copyright (c) 2001-2009 ElevenCraft Inc.
# See LICENSE for details.

import os
import sys

try:
    import _thread as thread_module
except ImportError:
    import thread as thread_module

## import louie

if sys.platform == 'win32' or os.environ.get('DISPLAY', '') != '':
    from schevo.gtk2.application import Application
    GTK_AVAILABLE = True
else:
    GTK_AVAILABLE = False

from schevo.script.command import Command
from schevo.script import opt


USAGE = """\
schevo gnav [options] [DBNAME]

DBNAME: The database alias (name).  If not specified you may open a
database using the File menu."""


def _parser():
    p = opt.parser(USAGE)
    p.add_option('-c', '--pycrust', dest='pycrust',
                 help='Open a PyCrust session in a separate thread.',
                 action='store_true', default=False,
                 )
    return p


def start_pycrust(**locals):
    """Start PyCrust in a separate thread."""
    import wx
    class App(wx.App):
        def OnInit(self):
            from wx import py
            wx.InitAllImageHandlers()
            self.frame = py.crust.CrustFrame(locals=locals)
            self.frame.SetSize((800, 600))
            self.frame.Show()
            self.SetTopWindow(self.frame)
            return True
    app = App(0)
    thread_module.start_new_thread(app.MainLoop, ())


class Navigator(Command):

    name = 'Database Navigator'
    description = 'Navigate Schevo databases using a GTK2 GUI.'

    def main(self, arg0, args):
        print()
        print()
        if GTK_AVAILABLE:
            parser = _parser()
            options, args = parser.parse_args(list(args))
            if args:
                db_alias = args.pop(0)
                #if not os.path.isfile(db_alias):
                #    print 'File %r must already exist' % db_alias
                #    return 1
            else:
                db_alias = None
            # Create PyGTK application.
            app = Application()
            # Open the database.
            if db_alias:
                #print 'Opened database', db_alias
                app.database_open(db_alias)
            # Start PyCrust if requested.
            if options.pycrust:
                start_pycrust(app=app)
                print('PyCrust started.')
            # Start PyGtk event loop.
            print('Starting Navigator UI...')
            app.run()
        else:
            print('GTK is not available.')
            return 1


start = Navigator
