"""prosper_version.py: utilities to help parse current version information

Props to ccpgames/setuputils for framework

"""
from codecs import decode
import os
from subprocess import check_output
import warnings

import semantic_version

import prosper.common.exceptions as exceptions

DEFAULT_VERSION = '0.0.0'
DEFAULT_BRANCH = 'master'
TEST_MODE = False

def get_version(
        here_path,
        default_version=DEFAULT_VERSION
):
    """tries to resolve version number

    Args:
        here_path (str): path to project local dir
        default_version (str, optional): what version to return if all else fails

    Returns:
        str: semantic_version information for library

    """
    if 'site-packages' in here_path:
        # Running as dependency
        return _version_from_file(here_path)

    if os.environ.get('TRAVIS_TAG'):
        # Running on Travis-CI: trumps all
        if not TEST_MODE:  # pragma: no cover
            return os.environ.get('TRAVIS_TAG').replace('v', '')
        else:
            warnings.warn(
                'Travis detected, but TEST_MODE enabled',
                exceptions.ProsperVersionTestModeWarning)

    try:
        current_tag = _read_git_tags(default_version=default_version)
    except Exception:  # pragma: no cover
        return _version_from_file(here_path)

    # TODO: if #steps from tag root, increment minor
    # TODO: check if off main branch and add name to prerelease

    with open(os.path.join(here_path, 'version.txt'), 'w') as v_fh:
        # save version info somewhere static
        v_fh.write(current_tag)

    return current_tag

def _read_git_tags(
        default_version=DEFAULT_VERSION,
        git_command=['git', 'tag']
):
    """tries to find current git tag

    Notes:
        git_command exposed for testing null case

    Args:
        default_version (str, optional): what version to make
        git_command (:obj:`list`, optional): subprocess command

    Retruns:
        str: latest version found, or default

    Raises:
        exceptions.ProsperDefaultVersionWarning: git version not found

    """
    try:  # pragma: no cover
        current_tags = check_output(git_command).splitlines()
    except Exception:
        raise

    if not current_tags[0]:
        warnings.warn(
            'Unable to resolve current version',
            exceptions.ProsperDefaultVersionWarning)
        return default_version

    latest_version = semantic_version.Version(default_version)
    for tag in current_tags:
        tag_str = decode(tag, 'utf-8').replace('v', '')
        try:
            tag_ver = semantic_version.Version(tag_str)
        except Exception:  # pragma: no cover
            continue  # invalid tags ok, but no release

        if tag_ver > latest_version:
            latest_version = tag_ver

    return str(latest_version)

def _version_from_file(
        path_to_version,
        default_version=DEFAULT_VERSION
):
    """for PyPI installed versions, just get data from file

    Args:
        path_to_version (str): abspath to dir where version.txt exists
        default_version (str, optional): fallback version in case of error

    Returns:
        str: current working version

    """
    version_filepath = os.path.join(path_to_version, 'version.txt')
    if not os.path.isfile(version_filepath):
        warnings.warn(
            'Unable to resolve current version',
            exceptions.ProsperDefaultVersionWarning)
        return default_version

    with open(version_filepath, 'r') as v_fh:
        data = v_fh.read()

    return data
