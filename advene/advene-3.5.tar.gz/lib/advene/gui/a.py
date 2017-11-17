#! /usr/bin/python

from evaluator import Evaluator
import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

w = Gtk.Window()

sw1 = Gtk.ScrolledWindow()
v = Gtk.VBox()
p = Gtk.Paned()
sw2 = Gtk.ScrolledWindow()
sw3 = Gtk.ScrolledWindow()
l1 = Gtk.Layout()
l1.set_size(2000, 200)
l2 = Gtk.Layout()
b1 = Gtk.Button.new_with_label("FOO")
b2 = Gtk.Button.new_with_label("BAR")
l1.put(b1, 1000, 100)
l2.put(b2, 100, 100)
sw2.add(l1)
sw3.add(l2)
p.add2(sw3)
p.add1(sw2)
l1.set_size_request(200, 200)
w.set_size_request(500, 200)
p.set_position(10)
v.add(p)
sw1.add(v)
w.add(sw1)

def debug_cb(*p):
    print(u" - ".join(str(e) for e in p))
    return False
p.connect('notify::position', debug_cb)

w.show_all()

ev = Evaluator(globals_=globals(), locals_=locals())
ev.run()
#Gtk.main ()
