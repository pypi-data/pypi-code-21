# -*- coding: utf-8 -*-
#
# Entry points for command line executable.
#
# @author <bprinty@gmail.com>
# ------------------------------------------------


# imports
# -------
import re
import os
import sys
import getpass
import subprocess
import paramiko
from ConfigParser import SafeConfigParser
from gems import filetree, composite


# decorators
# ----------
def local_context(func):
    def decorator(args):
        # configure directories
        try:
            args.base = run('git rev-parse --show-toplevel')
        except subprocess.CalledProcessError:
            sys.exit()
        args.home = os.path.expanduser('~')
        
        # set up remote list
        args.remotes = {}
        for line in run('git remote -v').split('\n'):
            if line != '':
                arr = line.split('\t')
                args.remotes[arr[0]] = re.sub(" (.*)$", "", arr[1])
        
        # set up data directory
        if os.path.isdir(os.path.join(args.base, '.git')):
            args.gitdir = os.path.join(args.base, '.git')
        else:
            with open(os.path.join(args.base, '.git'), 'r') as fi:
                dat = composite.load(fi)
            args.gitdir = os.path.realpath(os.path.join(args.base, dat.gitdir))
        args.exclude = os.path.join(args.gitdir, 'info', 'exclude')

        # set up config
        if os.path.exists(os.path.join(args.base, '.xfer')):
            args.config = os.path.join(args.base, '.xfer')
        else:
            args.config = os.path.join(args.gitdir, 'xfer')
        if not os.path.exists(args.config):
            open(args.config, 'a').close()
        if not os.path.exists(args.exclude):
            open(args.exclude, 'a').close()
        
        # read configs for each remote
        args.cache = []
        with open(args.config, 'r') as fi:
            args.cache = map(lambda x: x.rstrip(), fi.readlines())
        
        # run entry point
        args.update = False
        ret = func(args)

        # update configs that need to be updated
        if args.update:
            with open(args.config, 'w') as fo:
                fo.write('\n'.join(sorted(args.cache)))
            with open(args.exclude, 'w') as fo:
                fo.write('\n'.join(sorted(args.cache)))
        return ret
    return decorator


def remote_context(func):
    def decorator(args):
        if args.remote != 'local':
            if args.remotes.get(args.remote) is None:
                sys.exit('Remote does not exist!')

            url = args.remotes[args.remote]
            args.type = url.split(':')[0]
            if args.type == 'ssh':
                # parse config for remote info
                m = re.match(r"ssh://(.+)@(.+):(\d+)(.+).git", url)
                if not m:
                    sys.exit('Could not parse remote url.\nThe format should be: ssh://<user>@<host>:<port><path>')
                user, server, port, args.remote_base = m.groups()

                # connect via ssh
                args.ssh = paramiko.SSHClient()
                args.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                args.ssh.load_system_host_keys()
                logged_in = False
                try:
                    args.ssh.connect(server, username=user, port=int(port))
                    logged_in = True
                except paramiko.AuthenticationException:
                    for n in range(0, 3):
                        try:
                            password = getpass.getpass(prompt='Password: ', stream=None)
                            args.ssh.connect(server, username=user, password=password, port=int(port))
                            logged_in = True
                            break
                        except paramiko.AuthenticationException:
                            pass
                if not logged_in:
                    sys.exit('Could not connect to remote!')
                args.sftp = args.ssh.open_sftp()

                # configure remote
                ensure_remote(args.sftp, args.remote_base)
                if remote_isdir(args.sftp, os.path.join(args.remote_base, '.git')):
                    args.remote_gitdir = os.path.join(args.remote_base, '.git')
                elif remote_exists(args.sftp, os.path.join(args.remote_base, '.git')):
                    with args.sftp.open(os.path.join(args.remote_base, '.git'), 'r') as fi:
                        dat = composite.load(fi)
                    args.remote_gitdir = os.path.realpath(os.path.join(args.remote_base, dat.gitdir))
                else:
                    args.remote_gitdir = os.path.join(args.remote_base, '.git')
                    ensure_remote(args.sftp, args.remote_gitdir)
                args.remote_exclude = os.path.join(args.remote_gitdir, 'info', 'exclude')

                # config path
                if remote_exists(args.sftp, os.path.join(args.remote_base, '.xfer')):
                    args.remote_config = os.path.join(args.remote_base, '.xfer')
                else:
                    args.remote_config = os.path.join(args.remote_gitdir, 'xfer')

                # read remote cache
                args.remote_cache = []
                args.remote_update = False
                try:
                    with args.sftp.open(args.remote_config, 'r') as fi:
                        args.remote_cache = map(lambda x: x.rstrip(), fi.readlines())
                except IOError:
                    pass
            else:
                raise NotImplementedError('Remote type {} not currently supported!'.format(args.type))

        # run entry point
        ret = func(args)

        if args.remote != 'local':
            if args.type == 'ssh':
                # update remote cache
                if args.remote_update:
                    try:
                        with args.sftp.open(args.remote_config, 'w') as fo:
                            fo.write('\n'.join(args.remote_cache))
                        with args.sftp.open(args.remote_exclude, 'w') as fo:
                            fo.write('\n'.join(args.remote_cache))
                    except IOError:
                        pass

                # close connection
                args.sftp.close()
                args.ssh.close()
        return ret
    return decorator


# methods
# -------
def run(cmd, cwd=None):
    return subprocess.check_output(cmd, shell=True, cwd=cwd).rstrip()


def call(cmd, cwd=None):
    ret = subprocess.check_call(cmd, shell=True, cwd=cwd)
    if ret != 0:
        sys.exit('Something went wrong running "{}".'.format(cmd))
    return


def remote_exists(sftp, path):
    try:
        sftp.stat(path)
        return True
    except (IOError, paramiko.sftp.SFTPError):
        return False


def remote_isdir(sftp, path):
    try:
        sftp.chdir(path)
        return True
    except (IOError, paramiko.sftp.SFTPError):
        return False


def ensure_remote(sftp, path):
    if path == '/':
        sftp.chdir('/')
        return
    if path == '':
        return
    try:
        sftp.chdir(path)
    except IOError:
        dirname, basename = os.path.split(path.rstrip('/'))
        ensure_remote(sftp, dirname)
        sftp.mkdir(basename)
        sftp.chdir(basename)
        return True
    return


def ensure_local(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return


# entry points
# ------------
@local_context
def config(args):
    """
    Configure server transfer information.
    """
    uname = getpass.getuser()
    name = raw_input('Enter remote name (example: xfer): ') or 'xfer'
    if name in args.remotes:
        sys.exit('\n{} is already listed as a remote.\nPlease choose a different name or remove the remote using `git remote remove`\n'.format(name))
    if args.type == 'ssh':
        server = raw_input('Enter remote url (example: {}@localhost): '.format(uname)) or uname + '@localhost'
        repo = os.path.join(args.home, os.path.basename(args.base))
        dest = raw_input('Enter remote destination for repo (default: {}): '.format(repo)) or repo
        dest = dest.replace('.git', '')
        port = raw_input('Enter port for server (default: 22): ') or 22
        remote = 'ssh://{}:{}{}.git'.format(server, port, dest)
    elif args.type == 's3':
        server = raw_input('Enter remote bucket name (example: mybucket): '.format(uname)) or uname
        remote = 's3://{}'.format(server)
    elif args.type == 'gs':
        server = raw_input('Enter remote bucket name (example: mybucket): '.format(uname)) or uname
        remote = 'gs://{}'.format(server)
    else:
        sys.exit('No rule for processing server type: {}'.format(args.type))
    run('git remote add {} {}'.format(name, remote))
    return


@local_context
def add(args):
    """
    Add files to tracking.

    Args:
        args (obj): Arguments from command line.
    """
    files = []
    for path in args.files:
        if os.path.isdir(path):
            ft = filetree(path)
            files.extend(ft.filelist())
        else:
            files.append(path)
    for path in files:
        path = os.path.normpath(os.path.relpath(path, args.base))
        if path not in args.cache:
            args.cache.append(path)
    args.update = True
    return


@local_context
@remote_context
def list(args):
    """
    List currently tracked files.

    Args:
        args (obj): Arguments from command line.
    """
    if args.remote == 'local':
        if len(args.cache) > 0:
            sys.stdout.write('\n'.join(args.cache) + '\n')
    else:
        if len(args.remote_cache) > 0:
            sys.stdout.write('\n'.join(args.remote_cache) + '\n')
    return


@local_context
def prune(args):
    """
    Prune non-existing files from tracking.

    Args:
        args (obj): Arguments from command line.
    """
    keep = []
    for path in args.cache:
        if os.path.exists(path):
            keep.append(path)
        else:
            sys.stderr.write('Removing: {}'.format(path) + '\n')
    args.cache = keep
    args.update = True
    return


@local_context
def reset(args):
    """
    Reset tracking information for xfer.

    Args:
        args (obj): Arguments from command line.
    """
    if os.path.exists(args.config):
        os.remove(args.config)
    return


@local_context
def remove(args):
    """
    Remove files from tracking.

    Args:
        args (obj): Arguments from command line.
    """
    files = []
    for path in args.files:
        if os.path.isdir(path):
            ft = filetree(path)
            files.extend(ft.filelist())
        else:
            files.append(path)
    for path in files:
        relpath = os.path.normpath(os.path.relpath(path, args.base))
        if relpath in args.cache:
            del args.cache[args.cache.index(relpath)]
            if args.delete and os.path.exists(path):
                os.remove(path)
    args.update = True
    return


def rm(args):
    """
    Remove files from tracking and delete the file.

    Args:
        args (obj): Arguments from command line.
    """
    args.delete = True
    return remove(args)


@local_context
@remote_context
def diff(args):
    """
    Find difference between remote and local files.

    Args:
        args (obj): Arguments from command line.
    """
    local = set(args.cache)
    remote = set(args.remote_cache)
    here = local.difference(remote)
    for item in sorted(here):
        sys.stdout.write('< {}'.format(item) + '\n')
    there = remote.difference(local)
    for item in sorted(there):
        sys.stdout.write('> {}'.format(item) + '\n')
    return


@local_context
@remote_context
def push(args):
    """
    Push files to remote server.

    Args:
        args (obj): Arguments from command line.
    """
    if args.type == 'ssh':
        local = set(args.cache)
        for path in sorted(args.cache):
            if os.path.exists(os.path.join(args.base, path)) and not remote_exists(args.sftp, os.path.join(args.remote_base, path)):
                print('push: {}'.format(path))
                ensure_remote(args.sftp, os.path.dirname(os.path.join(args.remote_base, path)))
                args.sftp.put(
                    os.path.join(args.base, path),
                    os.path.join(args.remote_base, path)
                )
                args.remote_cache.append(path)
            args.remote_update = True
    elif args.type == 's3':
        raise NotImplementedError('s3:// remote type not yet supported!')
    elif args.type == 'gs':
        raise NotImplementedError('gs:// remote type not yet supported!')
    return


@local_context
@remote_context
def pull(args):
    """
    Pull files from remote server.

    Args:
        args (obj): Arguments from command line.
    """
    for path in sorted(args.remote_cache):
        if not os.path.exists(os.path.join(args.base, path)) and remote_exists(args.sftp, os.path.join(args.remote_base, path)):
            print('pull: {}'.format(path))
            ensure_local(os.path.dirname(os.path.join(args.base, path)))
            args.sftp.get(
                os.path.join(args.remote_base, path),
                os.path.join(args.base, path)
            )
            args.cache.append(path)
        args.update = True
    return

