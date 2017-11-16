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


@deploy('Copy')
def move(state, host, comment, src_file, dest_file, **kwargs):
    """Move a file."""

    # no source or destination
    if src_file is None:
        raise OperationError('source file not defined')
    if dest_file is None:
        raise OperationError('destination file not defined')

    kwargs.pop('sudo', None)
    server.shell(
        # {f"Copy {src} file to {dest}"},
        f"mv ./packer/{src_file} {dest_file}",
        sudo=True
    )
    files.file(
        # {f"Change file {dest} mode"},
        dest_file,
        **kwargs,
        sudo=True
    )
