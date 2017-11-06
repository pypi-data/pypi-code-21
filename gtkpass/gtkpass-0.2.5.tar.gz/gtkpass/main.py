import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os
from subprocess import call, Popen, PIPE, STDOUT

class GtkPassWindow(Gtk.Window):
    
    def __init__(self):
        self.search_text = ''
        self.search_result_text = ''
        self.get_pass_path()
        self.build_gui()
        self.build_data_structures()

    def get_pass_path(self):
        self.pass_path = os.path.expanduser('~/.password-store')

    def build_gui(self):
        Gtk.Window.__init__(self, title='pass')
        self.set_border_width(10)
        self.set_default_size(300, -1)
        self.text_view = Gtk.Entry()
        self.text_view.set_editable(False)
        self.text_view.set_can_focus(False)
        self.text_entry = Gtk.Entry()
        self.text_entry.connect('key-release-event', self.on_key_release)
        self.text_entry.connect('activate', self.on_activate)
        self.text_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,
                                                'system-search-symbolic')
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box.pack_start(self.text_view, True, True, 0)
        self.box.pack_start(self.text_entry, True, True, 0)
        self.add(self.box)
        self.text_entry.grab_focus()

    def build_data_structures(self):
        self.pass_list = []
        for root, dirs, files in os.walk(self.pass_path):
            for file_ in files:
                file_ = os.path.join(root, file_)
                if os.path.splitext(file_)[1] == '.gpg':
                    pass_list_item = os.path.relpath(file_, self.pass_path)
                    pass_list_item = os.path.splitext(pass_list_item)[0]
                    self.pass_list.append(pass_list_item)

    def fuzzy_find(self):
        p = Popen(['fzf', '-f', self.search_text],
                  stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        fzf_in = '\n'.join(self.pass_list).encode('utf-8')
        return p.communicate(fzf_in)[0].decode().strip().split('\n')

    def on_key_release(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
        self.search_text = self.text_entry.get_text().strip()
        if self.search_text == '':
            self.search_result_text = None
        else:
            search_result = self.fuzzy_find()
            if search_result == []:
                self.search_result_text = None
            else:
                self.search_result_text = search_result[0]
        if self.search_result_text:
            self.text_view.set_text(self.search_result_text)
        else:
            self.text_view.set_text('')

    def on_button_release(self, widget, event):
        self.copy_to_clipboard()

    def on_activate(self, event):
        self.copy_to_clipboard()

    def copy_to_clipboard(self):
        if self.search_result_text:
            p = call(['pass', '-c', self.search_result_text])
            self.text_entry.set_icon_from_icon_name(
                            Gtk.EntryIconPosition.SECONDARY,
                            'edit-paste-symbolic')


def main():
    win = GtkPassWindow()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
