#!/usr/bin/python
import os
import os.path as osp
import sys
import logging
import spur

_logger = logging.getLogger()


def parse_depfile(depfile, version, owner='vauxoo'):
    """ This method, parse plain text file oca_dependencies.txt,
    if you have valid repository name, url and version
    :param depfile: object type open file
    :return: Returns list of tuples [(repo, url, version)]
    """
    deps = []
    for line in depfile:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        repo = parts[0]
        if len(parts) > 2:
            branch = parts[2]
        else:
            branch = version
        if len(parts) > 1:
            url = parts[1]
        else:
            url = 'https://github.com/%s/%s.git' % (owner, repo)
        deps.append((repo, url, branch))
    return deps


def git_checkout(deps_checkout_dir, reponame, url, branch):
    """ This method downloads the repositories found in the oca_dependencies
    files and clones them in the specified dir. If he specified directory
    where the dependencies will be cloned already exists
    and is not empty it won't clone the repos
    :param deps_checkout_dir: he directory in which the dependency
    repositories will be cloned
    :param reponame: name for repository
    :param url: url address repository
    :param branch: branch or version repository
    :return: Returns list (full path)
    """
    checkout_dir = osp.join(deps_checkout_dir, reponame)
    if not osp.isdir(checkout_dir):
        command = ['git', 'clone', '-q', url, '-b', branch,
                   '--depth=1', checkout_dir]
        _logger.info('Calling %s', ' '.join(command))
        shell = spur.LocalShell()
        try:
            shell.run(command)
        except spur.RunProcessError as error:
            message_str = ("Could not clone repo {repo} "
                           "branch {branch}, error: {error} ").format(repo=url,
                                                                      branch=branch,
                                                                      error=error.stderr_output)
            return (False, message_str)

    return (True, checkout_dir)


def get_dep_filename(deps_checkout_dir, build_dir, file_name, version):
    """ This method, makes a recursive search directories to get all the
    files listed in the parameters file_name (oca_dependencies.txt)
    :param deps_checkout_dir: he directory in which the dependency
    repositories will be cloned
    :param build_dir: the directory in which the tested
     repositories have been cloned
    :param file_name: filename to be searched
    :return: Returns list with absolute paths
    """
    dependencies = []
    processed = set()
    depfilename = osp.join(build_dir, file_name)
    dependencies.append(depfilename)
    for repo in os.listdir(deps_checkout_dir):
        _logger.info('examining %s', repo)
        processed.add(repo)
        depfilename = osp.join(deps_checkout_dir, repo, file_name)
        dependencies.append(depfilename)
    for depfilename in dependencies:
        try:
            with open(depfilename) as depfile:
                deps = parse_depfile(depfile, version)
        except IOError:
            deps = []
        for depname, url, branch in deps:
            _logger.info('* processing %s', depname)
            if depname in processed:
                continue
            processed.add(depname)
            checkout_dir = git_checkout(deps_checkout_dir, depname,
                                        url, branch)
            if not checkout_dir[0]:
                return checkout_dir
            new_dep_filename = osp.join(checkout_dir[1], file_name)
            if new_dep_filename not in dependencies:
                dependencies.append(new_dep_filename)
    return (True, dependencies)


def run(deps_checkout_dir, build_dir, version):
    """ This method executes above methods
    :param deps_checkout_dir: he directory in which the dependency
    repositories will be cloned
    :param build_dir: the directory in which the tested
    repositories have been cloned
    """
    depens = get_dep_filename(deps_checkout_dir, build_dir, 'oca_dependencies.txt',
                              version)
    return depens


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], sys.argv[3])
