import os
import tempfile
import subprocess
from pathlib import Path


def pcall(cmd, args, env=None):
    try:
        return subprocess.check_call([cmd] + args, env=env)
    except OSError:
        raise OSError('command %r failed, it it in your PATH ?' % cmd)


def setup_local_pg_cluster(request, datadir, pgport):
    " create (if missing) a local cluster to use for the tests "
    dbpath = Path(datadir, 'pgdb')
    if not dbpath.exists():
        pcall('initdb', ['-D', dbpath.as_posix(), '-E', 'utf-8', '--locale=C'])
    env = os.environ.copy()
    sockdir = tempfile.mkdtemp(prefix='pgsocket')
    options = '-k %s -p %s' % (sockdir, pgport)
    options += ' -c fsync=off -c full_page_writes=off'
    options += ' -c synchronous_commit=off'
    pcall('pg_ctl', ['start', '-w', '-D', dbpath.as_posix(), '-o', options], env=env)

    def shutdown_postgres():
        pcall('pg_ctl', ['stop', '-D', dbpath.as_posix(), '-m', 'fast'])
        try:
            os.rmdir(sockdir)
        except OSError:
            pass
    request.addfinalizer(shutdown_postgres)
