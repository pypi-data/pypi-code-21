from __future__ import division, absolute_import, print_function, unicode_literals

import logging
logger = logging.getLogger(__name__)

from collections import OrderedDict

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except ImportError:
    print("ERR: GTK not available")
    sys.exit(1)
    
class DataPage(object):
    def __init__(self, notebook, name="Data"):
        """Make new notebook page and adds to notebook."""
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.combobox = Gtk.ComboBoxText()
        self.scroll = Gtk.ScrolledWindow(vexpand=True)
        self.textview = Gtk.TextView(cursor_visible=False, monospace=True,
                                     editable=False)
        self.scroll.add(self.textview)                             
        self.box.add(self.combobox)
        self.box.add(self.scroll)
        self.name = name
        self.buffers = {}
        
        self.combobox.connect('changed', self.combobox_changed)
        
        notebook.append_page(self.box, Gtk.Label(label=name))
    
    def add_exp(self, exp):
        """Add all data from exp to page."""
        for name, df in exp.df.items():
            self.combobox.append(id=name, text=name)
            self.buffers[name] = Gtk.TextBuffer()
            self.buffers[name].set_text(df.to_string())
            self.box.show_all()
        
        self.combobox.set_active(0)
    
    def clear_exps(self):
        self.combobox.remove_all()
        self.buffers = {}
        
    def combobox_changed(self, object):
        """Switch displayed data buffer."""
        try:
            self.textview.set_buffer(
                self.buffers[self.combobox.get_active_id()]
            )
        except KeyError:
            pass
        
class InfoPage(object):
    def __init__(self, notebook, name="Info"):
        """Make new notebook page and adds to notebook."""
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.buffer = Gtk.TextBuffer()
        self.scroll = Gtk.ScrolledWindow(vexpand=True)
        self.textview = Gtk.TextView(cursor_visible=False, monospace=True,
                                     editable=False, buffer=self.buffer)
        self.scroll.add(self.textview)
        self.box.add(self.scroll)
        
        self.name = name
        
        notebook.append_page(self.box, Gtk.Label(label=name))
        self.box.show_all()
        
    def clear(self):
        """Clear buffer"""
        self.buffer.set_text('')
    
    def set_text(self, text):
        self.buffer.set_text(text)
    
    def add_line(self, line):
        self.buffer.insert_at_cursor('{}\n'.format(line))