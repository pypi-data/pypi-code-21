from contextlib import contextmanager
import posixpath

from fabric.api import prefix, run, put
from fabric.contrib.files import exists


class VirtualEnv(object):

    def __init__(self, envpath, dependencies=()):
        self.envpath = envpath
        self.dependencies = dependencies
        self.runner = None

    def install(self):
        self.init()

        with self.activate():
            self.runner('pip install -U pip', pty=False)
            for d in self.dependencies:
                if d[-4:] == '.txt':
                    self.install_from_requirements(d)
                elif d[0] == '!':
                    # Custom command after exclamation mark
                    self.runner(d[1:])
                else:
                    # Python package
                    self.runner('pip install -U {}'.format(d), pty=False)

    def init(self):
        if not self.exists():
            self.runner('python3 -m venv {}'.format(self.envpath))

    @contextmanager
    def activate(self):
        raise NotImplementedError


class RemoteVirtualEnv(VirtualEnv):

    def __init__(self, envpath, dependencies=()):
        super(RemoteVirtualEnv, self).__init__(envpath, dependencies)
        self.runner = run

    def exists(self):
        return exists(self.envpath)

    def install_from_requirements(self, reqfile='requirements.txt'):
        with requirements_file(reqfile) as fname:
            self.runner('pip install -r {}'.format(fname), pty=False)

    @contextmanager
    def activate(self):
        activate = posixpath.join(self.envpath, 'bin/activate')
        if not exists(activate):
            raise OSError('Cannot activate virtualenv {}'.format(self.envpath))
        with prefix('. {}'.format(activate)):
            yield


@contextmanager
def requirements_file(fname):
    if exists(fname):
        yield fname
    else:
        target = posixpath.join('/tmp/', fname)
        put(fname, target)
        yield target
        run('rm {}'.format(target))
