"""
Usage: get-addons [-m] path1 [path2 ...]
Given a list  of paths, finds and returns a list of valid addons paths.
With -m flag, will return a list of modules names instead.
"""

import ast
import os
import sys
import fileinput

MANIFEST_FILES = ['__odoo__.py', '__openerp__.py', '__terp__.py', '__manifest__.py']


def is_module(path):
    """return False if the path doesn't contain an odoo module, and the full
    path to the module manifest otherwise"""

    if not os.path.isdir(path):
        return False
    files = os.listdir(path)
    filtered = [x for x in files if x in (MANIFEST_FILES + ['__init__.py'])]
    if len(filtered) == 2 and '__init__.py' in filtered:
        return os.path.join(
            path, next(x for x in filtered if x != '__init__.py'))
    else:
        return False


def is_installable_module(path):
    """return False if the path doesn't contain an installable odoo module,
    and the full path to the module manifest otherwise"""
    manifest_path = is_module(path)
    if manifest_path:
        manifest = ast.literal_eval(open(manifest_path).read())
        if manifest.get('installable', True):
            return manifest_path
    return False


def get_modules(path):
    # Avoid empty basename when path ends with slash
    if not os.path.basename(path):
        path = os.path.dirname(path)
    res = []
    if os.path.isdir(path):
        res = [x for x in os.listdir(path)
               if is_installable_module(os.path.join(path, x))]
    return res


def is_addons(path):
    res = get_modules(path) != []
    return res


def get_addons(path):
    """Walks a path a returns all the addons inside sorted according to its
    dependencies.

    :param path: The path to walk
    :type path: str

    :returns: All the found addons
    :rtype: list
    """
    addons = {}
    if not os.path.isdir(path):
        return []
    if is_addons(path):
        addons[path] = get_dependencies(path)
    for base, dirs, files in os.walk(path):
        for directory in dirs:
            dir_path = os.path.join(base, directory)
            if is_addons(dir_path):
                addons[dir_path] = get_dependencies(dir_path)
    sorted_addons = get_sorted_addons_by_level(addons)
    return sorted_addons


def get_dependencies(path):
    """Gets the dependencies of an addon reading the `oca_dependencies.txt` file.

    :param path: The addon path
    :rtype: str

    :returns: The dependency list
    :rtype: list
    """
    deps = []
    dep_path = os.path.join(path, 'oca_dependencies.txt')
    try:
        with open(dep_path) as dep:
            for line in dep:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                deps.append(line.split()[0])
    except IOError:
        return []
    return deps


def get_sorted_addons_by_level(addons):
    """Sorts a list of addons according to its level, and followed
    by its dependencies also sorted by level.

    It first sorts the addons using `sort_addons_by_level` and then
    it puts the dependencies after their parents. This to keep the addons
    with higher dependency level first and then its addons also sorted by
    level.

    :param addons: The addons with their dependencies.
    :type addons: dict

    :returns: The addons sorted by level
    :rtype: list

    Example::

        get_sorted_addons_by_level({
            "e": [],
            "r": ["x"],
            "c": [],
            "t": ["r", "c"],
            "x": ["e"],
        })

    Returns::

        ["t", "r", "c", "x", "e"]

    """
    sorted_addons = []
    addons_by_deps = sort_addons_by_level(addons)
    addons_by_deps = sorted(addons_by_deps.keys(),
                            key=lambda dep, addons=addons_by_deps: -addons.get(dep))
    for addon in addons_by_deps:
        if addon not in sorted_addons:
            sorted_addons.append(addon)
        for dep in addons.get(addon, []):
            dep_addon = os.path.join(os.path.dirname(addon), dep)
            if dep_addon not in sorted_addons:
                sorted_addons.append(dep_addon)
    return sorted_addons


def sort_addons_by_level(addons, _key=False, _res=False):
    """Reads a dict of addons with dependencies and assigns a "level" that represents
    how deep its dependencies go.

    :param addons: The addons with their dependencies.
    :type addons: dict

    :param _key: This is for recursion purposes. Do not pass when calling from the outside.
    :param _res: This is for recursion purposes. Do not pass when calling from the outside.

    :returns: The addons with the level
    :rtype: dict

    Example::

        sort_addons_by_level({
            "e": [],
            "r": ["x"],
            "c": [],
            "t": ["r", "c"],
            "x": ["e"],
        })

    Returns::

        {
            "t": 3,
            "r": 2,
            "x": 1,
            "c": 0,
            "e": 0,
        }

    In this example "t" depends on "r" that depends on "x" that depends on "e".
    There are three "levels" of dependencies below "t".
    """
    _res = _res or {}
    if not _key:
        for _key in addons:
            _res.update(sort_addons_by_level(addons, _key, _res))
        return _res
    if _res.get(_key, -1) > -1:
        return _res
    _res[_key] = 0
    for dep in addons.get(_key, []):
        _res.update(sort_addons_by_level(
            addons, os.path.join(os.path.dirname(_key), dep), _res))
    _res[_key] = (max([
        _res.get(os.path.join(os.path.dirname(_key), dep), -1)
        for dep in addons.get(_key, [])
    ] or [-1]) + 1)
    return _res


def main(argv=None):
    if argv is None:
        argv = sys.argv
    params = argv[1:]
    if not params:
        print(__doc__)
        return 1

    list_modules = False
    exclude_modules = []
    odoo_path = '/home/odoo/instance/odoo/addons'
    enterprise_path = False

    while params and params[0].startswith('-'):
        param = params.pop(0)
        if param == '-m':
            list_modules = True
        if param == '-e':
            exclude_modules = [x for x in params.pop(0).split(',')]

    func = get_modules if list_modules else get_addons
    paths = params[0].split(',')
    addons_paths = []
    for path in paths:
        addons_paths.append(func(path))
    res = [x for l in addons_paths for x in l if x not in exclude_modules]
    enterprise_path = [path for path in res if os.path.basename(path) == 'enterprise']
    [res.remove(path) for path in enterprise_path]
    addons_path = ",".join(enterprise_path + [odoo_path] + res)
    for line in fileinput.input('/home/odoo/.openerp_serverrc', inplace=True):
        if 'addons_path' in line:
            parts = line.split('=')
            new_str = '{field} = {addons}'.format(field=parts[0].strip(), addons=addons_path)
            print(new_str.replace('\n', ''))
        else:
            print(line.replace('\n', ''))


if __name__ == "__main__":
    sys.exit(main())
