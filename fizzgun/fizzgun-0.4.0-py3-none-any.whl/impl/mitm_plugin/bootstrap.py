from fizzgun.impl.mitm_plugin import MitmPlugin


def start():
    return MitmPlugin.INSTANCE.fizzgun_handler
