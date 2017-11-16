from fs.osfs import OSFS
from .model import File


def touch(f):
    with OSFS('/') as fs:
        fs.create(f.path.rel)


def mv(f, path_new, overwrite=True):
    with OSFS('/') as fs:
        fs.move(f.path.rel, path_new, overwrite)


def cp(f, path_new, overwrite=True):
    with OSFS('/') as fs:
        fs.copy(f.path.rel, path_new, overwrite)


def rm(f):
    with OSFS('/') as fs:
        fs.remove(f.path.rel)
