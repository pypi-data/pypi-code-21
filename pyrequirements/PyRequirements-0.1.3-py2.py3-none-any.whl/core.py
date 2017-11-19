import pip
import warnings
import itertools
from collections import OrderedDict

def freeze_version(*args, **kwargs):
    """
    freeze version from current environment
    :param args: package name
    :param kwargs: package name and version
    :return: LIST[str[]]
    """
    data_map = OrderedDict()
    package_index = {}
    result = []
    package_names = [v.lower() for v in args]
    package_name_vers = {k.lower(): v for k, v in kwargs.items()}
    for installed in pip.get_installed_distributions():
        package_index[installed.project_name.lower().strip()] = installed

    for pkg_name in itertools.chain(package_names, package_name_vers.keys()):
        pkg_name = pkg_name.lower().strip()
        if pkg_name not in package_index:
            warnings.warn("current python environment don't install required package: {}".format(pkg_name), UserWarning)
            data_map[pkg_name] = None
            continue
        if pkg_name in package_names:
            if pkg_name not in data_map:
                data_map[pkg_name] = {
                    'pkg': package_index[pkg_name],
                    'project_name': package_index[pkg_name].project_name
                }
            else:
                raise ReferenceError("duplicate requirement: {}".format(pkg_name))
        if pkg_name in package_name_vers:
            if pkg_name not in data_map:
                data_map[pkg_name] = {
                    'pkg': package_index[pkg_name],
                    'project_name': package_index[pkg_name].project_name,
                    'version': package_name_vers[pkg_name],  # kwargs version
                }
            else:
                raise ReferenceError("duplicate requirement: {}".format(pkg_name))

    for pkg_name, info in data_map.items():
        if info is None:
            print(pkg_name)
            result.append(pkg_name)
        elif "version" in info:
            result.append("{}{}".format(info['project_name'], info["version"]))
        else:
            result.append("{}=={}".format(info['project_name'], info["pkg"].version))
    return result

