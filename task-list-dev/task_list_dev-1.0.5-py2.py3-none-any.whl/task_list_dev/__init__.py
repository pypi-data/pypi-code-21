# coding: utf-8

from task_list_dev import tools


VERSION = (1, 0, 0, 'final', 0)


def get_version(*args, **kwargs):
    from task_list_dev.utils.version import get_version
    return get_version(*args, **kwargs)


__version__ = get_version(VERSION)
__author__ = "Henrique Luz Rodrigues"
__email__ = "henrique.lr89@gmail.com"
__url__ = "https://github.com/HenriqueLR/task-list-dev"
