import os
import os.path as path
import shutil


def prepare(fullpath, clean=True):
    if clean:
        if path.exists(fullpath):
            if path.isdir(fullpath):
                shutil.rmtree(fullpath)
            else:
                os.remove(fullpath)
        os.makedirs(fullpath, exist_ok=False)
    else:
        os.makedirs(fullpath, exist_ok=True)

