from .global_germanium_instance import *


def S(*argv, **kw):
    """
    Call the super selector from germanium.
    :param germanium: The germanium instance. If missing, uses the global get_instance()
    """
    germanium = None
    if "germanium" in kw:
        germanium = kw.get("germanium")
        kw.pop("germanium")

    if germanium:
        return germanium.S(*argv, **kw)

    if not get_instance():
        raise Exception("You need to start a browser first with open_browser()")

    return get_instance().S(*argv, **kw)
