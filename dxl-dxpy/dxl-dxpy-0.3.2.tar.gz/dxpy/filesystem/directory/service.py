from fs.osfs import OSFS
from .model import Directory


def mkdir(d, recreate=True):
    with OSFS('/') as fs:
        fs.makedirs(d.path.rel, recreate=recreate)


def mv(d, path_new):
    with OSFS('/') as fs:
        fs.movedir(d.path_rel, path_new)


def cp(d, path_new, create=True):
    with OSFS('/') as fs:
        fs.copydir(d.path.rel, path_new, create)


def rm(d):
    with OSFS('/') as fs:
        fs.removetree(d.path.rel)
