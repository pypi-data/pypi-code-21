# coding=utf-8
import os
import errno
import shutil


def create_dir(dirname):
    if not dirname or os.path.exists(dirname):
        return

    try:
        os.makedirs(dirname)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


def remove_dir(dirname):
    try:
        shutil.rmtree(dirname)
    except (OSError, IOError):
        pass


def flatten_dir(root_dir):
    root_walk = os.walk(root_dir)
    _, top_level_dirs, _ = next(root_walk)

    for dirpath, _, filenames in root_walk:
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            shutil.move(filepath, root_dir)

    for top_level_dir in top_level_dirs:
        remove_dir(os.path.join(root_dir, top_level_dir))
