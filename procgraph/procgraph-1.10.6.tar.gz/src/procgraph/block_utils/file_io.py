import os


def make_sure_dir_exists(filename):
    ''' Makes sure that the path to file exists, but creating directories. '''
    dirname = os.path.dirname(filename)
    # dir == '' for current dir
    if dirname != '' and not os.path.exists(dirname):
        os.makedirs(dirname)


def expand(filename):
    ''' Expands environment variables in the filename. '''
    filename = os.path.expandvars(filename)
    filename = os.path.expanduser(filename)
    return filename



