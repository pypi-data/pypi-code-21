import contextlib
import imp
import os
import re
import subprocess

from setuptools import setup
from setuptools.command.sdist import sdist

DATA_ROOTS = []
PROJECT = 'drophi'
VERSION_FILE = 'drophi/__init__.py'

def _get_output_or_none(args):
    try:
        return subprocess.check_output(args).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None

def _get_git_description():
    return _get_output_or_none(['git', 'describe'])

def _get_git_branches_for_this_commit():
    branches = _get_output_or_none(['git', 'branch', '-r', '--contains', 'HEAD'])
    split = branches.split('\n') if branches else []
    return [branch.strip() for branch in split]

def _is_on_releasable_branch(branches):
    return any([branch == 'origin/master' or branch.startswith('origin/hotfix') for branch in branches])

def _git_to_version(git):
    match = re.match(r'(?P<tag>[\d\.]+)-(?P<offset>[\d]+)-(?P<sha>\w{8})', git)
    if not match:
        version = git
    else:
        version = "{tag}.post0.dev{offset}".format(**match.groupdict())
    return version

@contextlib.contextmanager
def write_version():
    git_description = _get_git_description()
    git_branches = _get_git_branches_for_this_commit()
    version = _git_to_version(git_description) if git_description else None
    if git_branches and not _is_on_releasable_branch(git_branches):
        print("Forcing version to 0.0.1 because this commit is on branches {} and not a whitelisted branch".format(git_branches))
        version = '0.0.1'
    if not version:
        return
    with open(VERSION_FILE, 'w') as version_file:
        version_file.write('__version__ = "{}"\n'.format(version))

def _get_version_from_file():
    basedir = os.path.abspath(os.path.dirname(__file__))
    root = imp.load_source('__init__', os.path.join(basedir, PROJECT, '__init__.py'))
    return root.__version__

def _get_version_from_git():
    git_description = _get_git_description()
    git_branches = _get_git_branches_for_this_commit()
    version = _git_to_version(git_description) if git_description else None
    if git_branches and not _is_on_releasable_branch(git_branches):
        print("Forcing version to 0.0.1 because this commit is on branches {} and not a whitelisted branch".format(git_branches))
        version = '0.0.1'
    return version

def get_version():
    file_version = _get_version_from_file()
    git_version = _get_version_from_git()
    return (file_version == 'development' and git_version) or file_version

def get_data_files():
    data_files = []
    for data_root in DATA_ROOTS:
        for root, _, files in os.walk(data_root):
            data_files.append((os.path.join(PROJECT, root), [os.path.join(root, f) for f in files]))
    return data_files

def main():
    setup(
        name                 = "drophi",
        version              = get_version(),
        description          = "A client for interacting with docker daemon",
        url                  = "https://bitbucket.com/Authentise/drophi",
        long_description     = "A client for interacting with docker from Python",
        author               = "Authentise, Inc.",
        author_email         = "engineering@authentise.com",
        install_requires     = [
            'aiohttp>=2.0.7',
            'arrow>=0.10.0',
        ],
        extras_require       = {
            'develop': [
                'pylint==1.6.4',
                'sphinx==1.6.1',
                'sphinx-autobuild==0.6.0',
            ]
        },
        packages             = [
            "drophi",
            "drophi.types",
        ],
        package_data         = {
            "drophi"         : ["drophi/*"],
            "drophi.types"   : ["drophi/types/*"],
        },
        data_files           = get_data_files(),
        scripts              = ['bin/drophi'],
        include_package_data = True,
    )

if __name__ == "__main__":
    main()
