from .base import BaseHandler
from .base import BaseRefreshHandler


SERVER_TYPE_PATTERN = r"^\{[a-z]+\}server$"


class UploadRefreshHandler(BaseRefreshHandler):
    def _upload_directory(self, ssh_client, local_path, remote_path, variables):
        from jinja2 import FileSystemLoader
        from jinja2.sandbox import SandboxedEnvironment
        from os import lstat
        from os import readlink
        from os import walk
        from os.path import dirname
        from os.path import islink
        from os.path import join

        for root, directories, files in walk(local_path):
            for directory in directories:
                directory_local_path = join(root, directory)
                directory_local_stat = lstat(directory_local_path)
                directory_remote_path = join(remote_path, root[len(local_path):], directory).replace('\\', '/')

                try:
                    ssh_client.lstat(directory_remote_path)
                except IOError:
                    ssh_client.mkdir(
                        directory_remote_path,
                        mode=directory_local_stat.st_mode)
                    ssh_client.chown(
                        directory_remote_path,
                        directory_local_stat.st_uid, directory_local_stat.st_gid)
                    ssh_client.chmod(
                        directory_remote_path,
                        directory_local_stat.st_mode & 0x0FFF)
                    ssh_client.utime(
                        directory_remote_path,
                        (directory_local_stat.st_atime, directory_local_stat.st_mtime))

            for file in files:
                file_local_path = join(root, file)
                file_local_stat = lstat(file_local_path)

                if islink(file_local_path):
                    file_remote_path = join(remote_path + root[len(local_path):], file)

                    try:
                        ssh_client.remove(file_remote_path)
                    except IOError:
                        pass

                    ssh_client.symlink(file_remote_path, readlink(file_local_path))
                else:
                    if file_local_path.endswith('.~remote'):
                        pass
                    elif file_local_path.endswith('.~'):
                        file_remote_path = join(remote_path, root[len(local_path):], file[:-2]).replace('\\', '/')

                        try:
                            with ssh_client.open(file_remote_path, 'r') as result_file:
                                old_content = result_file.read().decode(encoding='utf-8', errors='replace')

                            ssh_client.remove(file_remote_path)
                        except IOError:
                            old_content = ''

                        with open(file_local_path, 'r') as template_file:
                            template_code = template_file.read()

                        loader = FileSystemLoader(dirname(file_local_path))
                        environment = SandboxedEnvironment(
                            trim_blocks=False,
                            lstrip_blocks=False,
                            keep_trailing_newline=True,
                            autoescape=False,
                            loader=loader)
                        environment.globals.update(variables)

                        template_context = {'old_content': old_content}
                        template_context.update(variables)
                        template = environment.from_string(template_code)
                        result_text = template.render(template_context)

                        with ssh_client.open(file_remote_path, 'w') as result_file:
                            result_file.write(result_text)
                    else:
                        file_remote_path = join(remote_path, root[len(local_path):], file).replace('\\', '/')

                        try:
                            ssh_client.remove(file_remote_path)
                        except IOError:
                            pass

                        ssh_client.put(file_local_path, file_remote_path)

                ssh_client.chmod(file_remote_path, file_local_stat.st_mode & 0x0FFF)
                ssh_client.chown(file_remote_path, file_local_stat.st_uid, file_local_stat.st_gid)
                ssh_client.utime(file_remote_path, (file_local_stat.st_atime, file_local_stat.st_mtime))

    def fore_children(self, phase, settings, variables):
        from os.path import abspath
        from os.path import isdir
        from errno import ENOTDIR
        from os import strerror

        if self._resource.state == 0:
            server_resource = self._resource.get_ancestor(SERVER_TYPE_PATTERN)
            ssh_client = server_resource._ssh_client
            local_path = abspath(self._resource.properties['local-path'])
            remote_path = self._resource.properties['remote-path']
            ignore_missing = self._resource.properties.get('ignore-missing', '0').lower() in ('1', 'yes', 'true')

            if not isdir(local_path) and not ignore_missing:
                raise NotADirectoryError(ENOTDIR, strerror(ENOTDIR), local_path)

            self._upload_directory(ssh_client, local_path, remote_path, variables)


class UploadHandler(BaseHandler):
    def __init__(self, resource):
        super().__init__(UploadRefreshHandler, None, resource)


class ExecuteRefreshHandler(BaseRefreshHandler):
    def fore_children(self, phase, settings, variables):
        from ..utility import sync_print

        if self._resource.state == 0:
            server_resource = self._resource.get_ancestor(SERVER_TYPE_PATTERN)
            ssh_client = server_resource._ssh_client
            command = self._resource.properties['command']
            exit_status, stdout, stderr = ssh_client.execute(command)

            if exit_status == 0:
                text = '\033[32;1m{0}\033[0m = \033[30;1m{1}\033[0m\n'.format(exit_status, command)
            else:
                text = '\033[31;1m{0}\033[0m = \033[30;1m{1}\033[0m\n'.format(exit_status, command)

            if stderr:
                text += '\033[31;1m{0}\033[0m\n'.format(stderr)

            if stdout:
                text += '\033[32;1m{0}\033[0m\n'.format(stdout)

            sync_print(text, end='')


class ExecuteHandler(BaseHandler):
    def __init__(self, resource):
        super().__init__(ExecuteRefreshHandler, None, resource)
