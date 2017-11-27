import fileutils
import os


class _Cache:
    _units = []


def get_units_list():
    if _Cache._units:
        return _Cache._units
    units = []
    all_files = []
    if os.path.isdir(fileutils.root_dir + '/Resources/ini/units/creep/'):
        all_files.extend(fileutils.getFilesList(fileutils.root_dir + '/Resources/ini/units/creep/', False))
        all_files.extend(fileutils.getFilesList(fileutils.root_dir + '/Resources/ini/units/tower/', False))
        all_files.extend(fileutils.getFilesList(fileutils.root_dir + '/Resources/ini/units/hero/', False))
    all_files.extend(fileutils.getFilesList(fileutils.root_dir + '/Resources/ini/units/', False))
    for file in all_files:
        if file.startswith('_'):
            continue
        if not file.endswith('.xml'):
            continue
        name = file[0: -4]
        if name in ['death', 'death2']:
            continue
        units.append(name)
    _Cache._units = units
    return units
