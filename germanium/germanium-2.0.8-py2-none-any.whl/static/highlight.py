from germanium.util import highlight_g
from .global_germanium_instance import *


def highlight(selector, show_seconds=2, *args, **kw):
    """
    Highlights the given element, for easier debug.
    """
    if not get_instance():
        raise Exception("You need to start a browser first with open_browser()")

    console = False
    if "console" in kw:
        console = kw.get("console")
        kw.pop("console")

    return highlight_g(get_instance(), selector, show_seconds=2, *args, console=console, **kw)
