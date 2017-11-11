from .base import BaseDestroyHandler
from .base import BaseHandler
from .base import BaseRefreshHandler
from .linode_utility import _linode_client_init
from .linode_utility import _linode_disk_create
from .linode_utility import _linode_disk_delete
from .linode_utility import _linode_disk_select
from .linode_utility import _linode_server_config
from .linode_utility import _linode_server_create
from .linode_utility import _linode_server_delete
from .linode_utility import _linode_server_ensure_running
from .linode_utility import _linode_server_select
from .linode_utility import _linode_volume_create
from .linode_utility import _linode_volume_delete
from .linode_utility import _linode_volume_select


LINODE_SERVER_TYPE_PATTERN = r"^\{linode\}server$"
LINODE_DISK_TYPE_PATTERN = r"^\{linode\}disk$"
LINODE_VOLUME_TYPE_PATTERN = r"^\{linode\}volume$"


class SshClient(object):
    def _ensure_connection(self):
        from os.path import abspath
        from paramiko import Transport
        from paramiko.dsskey import DSSKey
        from paramiko.ecdsakey import ECDSAKey
        from paramiko.rsakey import RSAKey
        from paramiko.ssh_exception import SSHException
        from socket import AF_INET
        from socket import SOCK_STREAM
        from socket import socket

        private_key_path = abspath(self._settings['ssh_client']['private_key_path'])

        for private_key_class in (RSAKey, DSSKey, ECDSAKey):
            try:
                self._private_key = private_key_class.from_private_key_file(private_key_path)
            except SSHException as e:
                saved_exception = e

        if self._private_key is None:
            raise saved_exception

        while True:
            try:
                if self._transport:
                    try:
                        self._transport.renegotiate_keys()

                        return
                    except:
                        self._transport = None

                if not self._transport:
                    _linode_server_ensure_running(self._resource)

                self._socket = socket(AF_INET, SOCK_STREAM)
                self._socket.settimeout(2)
                self._socket.connect((self._resource.ipv4, 22))
                self._transport = Transport(self._socket)
                self._transport.use_compression(compress=True)
                self._transport.start_client()
                self._transport.auth_publickey('root', self._private_key)
                self._sftp = self._transport.open_sftp_client()

                return
            except:
                if self._sftp:
                    self._sftp.close()

                if self._transport:
                    self._transport.close()

                if self._socket:
                    self._socket.close()
                    self._socket = None

    def __init__(self, resource, settings, variables):
        self._resource = resource
        self._socket = None
        self._transport = None
        self._sftp = None
        self._settings = settings
        self._variables = variables
        self._private_key = None

    def execute(self, command, wait_for_output=True):
        from io import StringIO
        from time import sleep

        self._ensure_connection()

        try:
            channel = self._transport.open_session(timeout=2)
            channel.settimeout(2)
            channel.exec_command(command)

            stdout = StringIO()
            stderr = StringIO()

            while not channel.exit_status_ready():
                if channel.recv_stderr_ready():
                    stderr.write(channel.recv_stderr(65536).decode(encoding='utf-8', errors='ignore'))

                if channel.recv_ready():
                    stdout.write(channel.recv(65536).decode(encoding='utf-8', errors='ignore'))

            exit_status = channel.recv_exit_status()
            wait_time = 2.0 if wait_for_output else 0.2

            while ((stderr.tell() == 0) or (stdout.tell() == 0)) and (wait_time > 0.0):
                wait_time -= 0.1
                sleep(0.1)

                if channel.recv_stderr_ready():
                    stderr.write(channel.recv_stderr(65536).decode(encoding='utf-8', errors='ignore'))

                if channel.recv_ready():
                    stdout.write(channel.recv(65536).decode(encoding='utf-8', errors='ignore'))

            return exit_status, stdout.getvalue(), stderr.getvalue()
        finally:
            if channel:
                channel.close()

    def listdir(self, path='.'):
        self._ensure_connection()

        return self._sftp.listdir(path)

    def listdir_attr(self, path='.'):
        self._ensure_connection()

        return self._sftp.listdir_attr(path)

    def listdir_iter(self, path='.', read_aheads=50):
        self._ensure_connection()

        return self._sftp.listdir_iter(path, read_aheads)

    def open(self, filename, mode='r', bufsize=-1):
        self._ensure_connection()

        return self._sftp.open(filename, mode, bufsize)

    def remove(self, path):
        self._ensure_connection()

        return self._sftp.remove(path)

    def rename(self, oldpath, newpath):
        self._ensure_connection()

        return self._sftp.rename(oldpath, newpath)

    def posix_rename(self, oldpath, newpath):
        self._ensure_connection()

        return self._sftp.posix_rename(oldpath, newpath)

    def mkdir(self, path, mode):
        self._ensure_connection()

        return self._sftp.mkdir(path, mode)

    def rmdir(self, path):
        self._ensure_connection()

        return self._sftp.rmdir(path)

    def stat(self, path):
        self._ensure_connection()

        return self._sftp.stat(path)

    def lstat(self, path):
        self._ensure_connection()

        return self._sftp.lstat(path)

    def symlink(self, source, dest):
        self._ensure_connection()

        return self._sftp.symlink(source, dest)

    def chmod(self, path, mode):
        self._ensure_connection()

        return self._sftp.chmod(path, mode)

    def chown(self, path, uid, gid):
        self._ensure_connection()

        return self._sftp.chown(path, uid, gid)

    def utime(self, path, times):
        self._ensure_connection()

        return self._sftp.utime(path, times)

    def truncate(self, path, size):
        self._ensure_connection()

        return self._sftp.truncate(path, size)

    def readlink(self, path):
        self._ensure_connection()

        return self._sftp.readlink(path)

    def normalize(self, path):
        self._ensure_connection()

        return self._sftp.normalize(path)

    def chdir(self, path=None):
        self._ensure_connection()

        return self._sftp.chdir(path)

    def getcwd(self):
        self._ensure_connection()

        return self._sftp.getcwd()

    def putfo(self, file_object, remotepath, file_size=0, callback=None, confirm=True):
        self._ensure_connection()

        return self._sftp.putfo(file_object, remotepath, file_size, callback, confirm)

    def put(self, localpath, remotepath, callback=None, confirm=True):
        self._ensure_connection()

        return self._sftp.put(localpath, remotepath, callback, confirm)

    def getfo(self, remotepath, file_object, callback=None):
        self._ensure_connection()

        return self._sftp.getfo(remotepath, file_object, callback)

    def get(self, remotepath, localpath, callback=None):
        self._ensure_connection()

        return self._sftp.get(remotepath, localpath, callback)


class ServerRefreshHandler(BaseRefreshHandler):
    def try_sync(self, phase, settings, variables):
        _linode_client_init(settings)

        _linode_server_select(self._resource)
        self._resource._ssh_client = SshClient(self._resource, settings, variables)

        if not self._resource._linode_object:
            self._resource.id = None
            self._resource.code = None
            self._resource.ipv4 = None
            self._resource.ipv6 = None

            return False

        self._resource.code = getattr(self._resource._linode_object, 'label', None)
        self._resource.ipv4 = getattr(self._resource._linode_object, 'ipv4', [None])[0]
        self._resource.ipv6 = getattr(self._resource._linode_object, 'ipv6', None)

        return True

    def fore_children(self, phase, settings, variables):
        if self._resource.is_dirty:
            _linode_server_create(self._resource)

    def post_phase(self, phase, settings, variables):
        if phase.path == self._resource.phase.parent.path:
            if self._resource._linode_device_changed:
                self._resource._linode_object.invalidate()

                _linode_server_config(self._resource, self._resource._linode_devices)


class ServerDestroyHandler(BaseDestroyHandler):
    def __init__(self, resource):
        super().__init__(resource)
        self._resource._linode_devices = [None for i in range(0, 8)]
        self._resource._linode_device_changed = False

    def try_sync(self, phase, settings, variables):
        _linode_client_init(settings)

        _linode_server_select(self._resource)

        if not self._resource._linode_object:
            self._resource.id = None
            self._resource.code = None
            self._resource.ipv4 = None
            self._resource.ipv6 = None

            return False

        return True

    def fore_children(self, phase, settings, variables):
        if self._resource.is_dirty:
            _linode_server_delete(self._resource)


class ServerHandler(BaseHandler):
    def __init__(self, resource):
        super().__init__(ServerRefreshHandler, ServerDestroyHandler, resource)


class DiskRefreshHandler(BaseRefreshHandler):
    def try_sync(self, phase, settings, variables):
        _linode_client_init(settings)

        server_resource = self._resource.get_ancestor(LINODE_SERVER_TYPE_PATTERN)
        _linode_disk_select(server_resource, self._resource)

        if not self._resource._linode_object:
            self._resource.id = None
            self._resource.code = None
            self._resource.ipv4 = None
            self._resource.ipv6 = None

            return False

        self._resource.code = getattr(self._resource._linode_object, 'label', None)

        return True

    def fore_children(self, phase, settings, variables):
        if self._resource.is_dirty:
            server_resource = self._resource.get_ancestor(LINODE_SERVER_TYPE_PATTERN)

            if not self._resource.id:
                _linode_disk_create(server_resource, self._resource)
                server_resource._linode_device_changed = True
                self._resource.id = self._resource._linode_object.id
                self._resource.code = getattr(self._resource._linode_object, 'label', None)
                self._resource.ipv4 = getattr(self._resource._linode_object, 'ipv4', [None])[0]
                self._resource.ipv6 = getattr(self._resource._linode_object, 'ipv6', None)

    def post_children(self, phase, settings, variables):
        server_resource = self._resource.get_ancestor(LINODE_SERVER_TYPE_PATTERN)
        index = int(self._resource.properties.get('index', 0))

        self._resource._linode_object.invalidate()
        server_resource._linode_devices[index] = self._resource._linode_object


class DiskDestroyHandler(BaseDestroyHandler):
    def try_sync(self, phase, settings, variables):
        _linode_client_init(settings)

        server_resource = self._resource.get_ancestor(LINODE_SERVER_TYPE_PATTERN)
        _linode_disk_select(server_resource, self._resource)

        if not self._resource._linode_object:
            self._resource.id = None
            self._resource.code = None
            self._resource.ipv4 = None
            self._resource.ipv6 = None

            return False

        return True

    def fore_children(self, phase, settings, variables):
        if self._resource.is_dirty:
            server_resource = self._resource.get_ancestor(LINODE_SERVER_TYPE_PATTERN)

            if server_resource._linode_object:
                if self._resource._linode_object:
                    self._resource._linode_object.invalidate()

                    _linode_disk_delete(server_resource, self._resource)


class DiskHandler(BaseHandler):
    def __init__(self, resource):
        super().__init__(DiskRefreshHandler, DiskDestroyHandler, resource)


class VolumeRefreshHandler(BaseRefreshHandler):
    def try_sync(self, phase, settings, variables):
        _linode_client_init(settings)

        server_resource = self._resource.get_ancestor(LINODE_SERVER_TYPE_PATTERN)
        _linode_volume_select(server_resource, self._resource)

        if not self._resource._linode_object:
            self._resource.id = None
            self._resource.code = None
            self._resource.ipv4 = None
            self._resource.ipv6 = None

            return False

        self._resource.code = getattr(self._resource._linode_object, 'label', None)

        return True

    def fore_children(self, phase, settings, variables):
        if self._resource.is_dirty:
            server_resource = self._resource.get_ancestor(LINODE_SERVER_TYPE_PATTERN)

            if not self._resource.id:
                _linode_volume_create(server_resource, self._resource)
                server_resource._linode_device_changed = True
                self._resource.id = self._resource._linode_object.id
                self._resource.code = getattr(self._resource._linode_object, 'label', None)
                self._resource.ipv4 = getattr(self._resource._linode_object, 'ipv4', [None])[0]
                self._resource.ipv6 = getattr(self._resource._linode_object, 'ipv6', None)

    def post_children(self, phase, settings, variables):
        server_resource = self._resource.get_ancestor(LINODE_SERVER_TYPE_PATTERN)
        index = int(self._resource.properties.get('index', 0))

        self._resource._linode_object.invalidate()
        server_resource._linode_devices[index] = self._resource._linode_object


class VolumeDestroyHandler(BaseDestroyHandler):
    def try_sync(self, phase, settings, variables):
        _linode_client_init(settings)

        server_resource = self._resource.get_ancestor(LINODE_SERVER_TYPE_PATTERN)
        _linode_volume_select(server_resource, self._resource)

        if not self._resource._linode_object:
            self._resource.id = None
            self._resource.code = None
            self._resource.ipv4 = None
            self._resource.ipv6 = None

            return False

        return True

    def fore_children(self, phase, settings, variables):
        if self._resource.is_dirty:
            server_resource = self._resource.get_ancestor(LINODE_SERVER_TYPE_PATTERN)

            if server_resource._linode_object:
                if self._resource._linode_object:
                    self._resource._linode_object.invalidate()

                    _linode_volume_delete(server_resource, self._resource)


class VolumeHandler(BaseHandler):
    def __init__(self, resource):
        super().__init__(VolumeRefreshHandler, VolumeDestroyHandler, resource)
