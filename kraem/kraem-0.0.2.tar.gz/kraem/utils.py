import platform
from os import path


def get_platform():
    return platform.system().lower()


# stolen from
# https://codereview.stackexchange.com/questions/20428/accessing-the-contents-of-a-projects-root-directory-in-python
MAIN_DIRECTORY = path.dirname(path.dirname(__file__))


def get_full_path(*pth):
    return path.join(MAIN_DIRECTORY, *pth)
