from pyinfra.api import FactBase, deploy
from pyinfra.api.exceptions import OperationError
from pyinfra.modules import files, server


class PythonVersion(FactBase):
    """get python version"""

    def command(self):
        return 'cat /usr/local/lib/pyenv/_pyenv/version'

    def process(self, output):
        return output[0].strip()


class NginxVersion(FactBase):
    '''
    Returns the nginx version installed.
    '''

    def command(self):
        return "nginx -v 2>&1"

    def process(self, output):
        return str(output[0].split('/')[1].split()[0]).strip()


class UwsgiVersion(FactBase):
    '''
    Returns the nginx version installed.
    '''

    def command(self):
        return "uwsgi --version"

    def process(self, output):
        return str(output[0]).strip()


@deploy('Move a file')
def move(state, host, src=None, dest=None, user=None, group=None, mode=None):
    # no source or destination
    if src is None:
        raise OperationError('source file not defined')
    if dest is None:
        raise OperationError('destination file not defined')

    server.shell(
        {f"Copy {src} file to {dest}"},
        f"mv ./packer/{src} {dest}",
        sudo=True
    )
    files.file(
        {f"Change file {dest} mode"},
        dest,
        user=user, group=group, mode=mode,
        sudo=True
    )
