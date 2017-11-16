import logging
logger = logging.getLogger(__name__)

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except ImportError:
    print "ERR: GTK not available"
    sys.exit(1)
    
from matplotlib.backends.backend_gtk3 \
    import NavigationToolbar2GTK3 as NavigationToolbar
    
def clear_notebook(notebook):
    for pages in range(notebook.get_n_pages()):
        notebook.remove_page(0)
        
def add_exp_to_notebook(notebook, exp):
    for plot in exp.plots:
        label = Gtk.Label.new(plot.name)
        notebook.append_page(plot.box, label)
        plot.box.show_all()

def replace_notebook_exp(notebook, exp, window):
    clear_notebook(notebook)
    add_exp_to_notebook(notebook, exp)
    add_navigation_toolbars(exp, window)

def add_navigation_toolbars(exp, window):
    for plot in exp.plots:
        toolbar = NavigationToolbar(plot.canvas, window)
        plot.box.pack_start(toolbar, expand=False, fill=False, padding=0)