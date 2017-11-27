import logging
from itertools import chain
from collections import ChainMap
from .doc import Doc
from ..signature import Signature

logger = logging.getLogger(__name__)

WIDTH = 300
MARGIN = 20
SPINNER = WIDTH - MARGIN * 2

DEFAULT_NAME = 'Horetu program'

def gtk(program,
        handlers=None, freedesktop=False,
        ):
    '''
    Run a GTK application.

    :type program: Program, callable, list, or dict
    :param program: The program for which to produce the interface
    :param dict handlers: Mapping from content type to handler program
    :param bool freedesktop: Fall back to xdg-open if a handler is not available
    '''
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
    except ImportError:
        logger.error('PyGObject is not installed; run this: pip install horetu[gui]')
    else:
        if not isinstance(program, Program):
            program = Program(program)
        if not program.name:
            program.name = DEFAULT_NAME
        class Window(Gtk.Window):
            handlers = handlers or {}
            freedesktop = freedesktop
            program = program
            def __init__(self):
                Gtk.Window.__init__(self, title=program.name)
                main(self, program)
        win = Window(function)
        win.connect("delete-event", Gtk.main_quit)
        win.show_all()
        Gtk.main()



def _init(self, function):
    # Base layout
    self.set_border_width(10)
    box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                        spacing=6)
    self.add(box_outer)

    # Inputs
    listbox = Gtk.ListBox()
    listbox.set_selection_mode(Gtk.SelectionMode.NONE)
    box_outer.pack_start(listbox, True, True, 0)

    s = Signature(function, with_help=False)
    fdoc = Doc(function)
    captions = dict(ChainMap(dict(fdoc.args), dict(fdoc.kwargs)))
    def arg(x):
        listbox.add(_param_row(x, captions[x.name]))
    for x in s.positional:
        arg(x)
    listbox.add(Gtk.HSeparator())
    for x in chain(s.keyword1, s.keyword2.values()):
        arg(x)
#   if s.var_positional:
#       listbox.add(_param_row(s.var_positional))

    # Output
    stack = Gtk.Stack()
    
    spinner = Gtk.Spinner()
    spinner.set_size_request(SPINNER, SPINNER)
    spinner.start()

    button_go = Gtk.ToolButton()
    button_go.set_icon_name('media-playback-start')
    button_go.connect('clicked', lambda x:
        stack.set_visible_child(spinner))

    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    self.textview = Gtk.TextView()
    self.textbuffer = self.textview.get_buffer()
    self.textbuffer.set_text('These are the output messages')
    scrolledwindow.add(self.textview)

    stack.add_titled(button_go, "go", "Go Button")
    stack.add_titled(spinner, "running", "Running")
    stack.add_titled(scrolledwindow, "output", "Program Output")
    box_outer.pack_start(stack, True, True, 0)

def _param_row(param, documentation):
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    label1 = Gtk.Label(xalign=0)
    label1.set_markup("<b>%s</b>" % param.name)
    label2 = Gtk.Label(xalign=0)
    label2.set_markup("<i>%s</i>" % documentation)
    vbox.pack_start(label1, True, True, 0)
    vbox.pack_start(label2, True, True, 0)

    row = Gtk.ListBoxRow()
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
    row.add(hbox)
    hbox.pack_start(vbox, True, True, 0)

    if param.takes_parameter:
        pass
    else:
        switch = Gtk.Switch()
        switch.props.valign = Gtk.Align.CENTER
        hbox.pack_start(switch, False, True, 0)

    return row
