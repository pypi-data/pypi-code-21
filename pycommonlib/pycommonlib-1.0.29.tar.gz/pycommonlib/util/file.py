import os
import shutil


def copytree(src, dst, symlinks=False):
    names = os.listdir(src)
    os.makedirs(dst, exist_ok=True)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                shutil.copy(srcname, dstname)
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
        except Error as err:
            errors.extend(err.args[0])
    if errors:
        raise Error(errors)