from .conf import Conf


def get_requirements():
    conf = Conf()
    return conf.get_freeze_requirements()
