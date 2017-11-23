import os
from typing import Optional
from buildlib.utils import semver


def extract_version_from_wheel_name(name: str) -> str:
    """
    Get the version part out of the wheel file name.
    """
    parted: list = name.split('-')
    return '' if len(parted) < 2 else parted[1]


def find_python_wheel(
    wheel_dir: str,
    semver_num: Optional[str] = None,
    wheelver_num: Optional[str] = None,
    raise_not_found: Optional[bool] = False,
) -> Optional[str]:
    """
    Search dir for a wheel-file which contains a specific version number in its
    name. Return found wheel name or False.
    """

    if wheelver_num:
        requested_version: str = wheelver_num

    elif semver_num:
        requested_version: str = semver.convert_semver_to_wheelver(semver_num)

    else:
        raise ValueError(
            'No version provided. Please provide either semver_num or '
            'wheelver_num.'
        )

    files: list = [file for file in os.listdir(wheel_dir)]

    matches: list = [
        file
        for file
        in files
        if extract_version_from_wheel_name(file) == requested_version
    ]

    if matches:
        return wheel_dir + '/' + matches[0]

    elif not matches and raise_not_found:
        raise FileNotFoundError('Could not find wheel file.')

    else:
        return None
