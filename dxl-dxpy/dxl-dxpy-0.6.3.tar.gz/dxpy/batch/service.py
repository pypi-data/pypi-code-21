import rx
from fs import copy, path


def files_in_directories(fs, include_dirs, include_files, depth=0, exclude_dirs=None, exclude_files=None):
    """
    Args:
    """
    from .model.filters import FilesFilter, DirectoriesFilter
    if not isinstance(include_dirs, (list, tuple)):
        raise TypeError(
            'include_dirs should be list or tuple of str, not {}.'.format(type(include_dirs)))
    if not isinstance(include_files, (list, tuple)):
        raise TypeError(
            'include_dirs should be list or tuple of str, not {}.'.format(type(include_files)))
    results = list()    
    (DirectoriesFilter(include_dirs, exclude_dirs, depth).obv(fs)
     .flat_map(lambda p: FilesFilter(include_files, exclude_files).obv(fs, p))
     .subscribe(results.append))
    return results


def sub_directories(fs, part_of_name):
    from .model import DirectoriesFilter
    """
    A helper function for filtering directories, which is equviliant to filtering directories of pattern:
        [part_of_name, part_of_name*]
    """
    return DirectoriesFilter([part_of_name, '{n}*'.format(part_of_name)]).lst(fs)
