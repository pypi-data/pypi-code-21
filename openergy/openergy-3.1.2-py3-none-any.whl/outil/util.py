import os
import stat

DEFAULT_SERVER_PERMS = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP


def mkdir(path):
    os.mkdir(path, DEFAULT_SERVER_PERMS)
