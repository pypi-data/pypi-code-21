from pyinfra.api import FactBase, operation
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


@operation
def move(comment, src, dest, user=None, group=None, mode=None):
    f""" {comment} """
    server.shell(
        f"mv {src} {dest}",
        sudo=True
    )
    files.file(
        dest,
        user=user, group=group, mode=mode,
        sudo=True
    )
