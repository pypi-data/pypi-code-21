from collections import OrderedDict

from ievv_opensource.utils.shellcommandmixin import ShellCommandError
from .abstract_npm_installer import AbstractNpmInstaller


class NpmInstallerError(Exception):
    pass


class PackageJsonDoesNotExist(NpmInstallerError):
    pass


class NpmInstaller(AbstractNpmInstaller):
    """
    NPM installer.
    """
    name = 'npminstall'
    optionprefix = 'npm'

    def __init__(self, *args, **kwargs):
        super(NpmInstaller, self).__init__(*args, **kwargs)
        self.queued_packages = OrderedDict()

    def log_shell_command_stderr(self, line):
        if 'npm WARN package.json' in line:
            return
        super(NpmInstaller, self).log_shell_command_stderr(line)

    def install_packages_from_packagejson(self):
        try:
            self.run_shell_command('npm',
                                   args=['install'],
                                   _cwd=self.app.get_source_path())
        except ShellCommandError:
            self.get_logger().command_error('npm install FAILED!')
            raise SystemExit()

    def install_npm_package(self, package, properties):
        package_spec = package
        if properties['version']:
            package_spec = '{package}@{version}'.format(
                package=package, version=properties['version'])
        args = ['install', package_spec]
        if properties['installtype'] is None:
            args.append('--save')
        else:
            args.append('--save-{}'.format(properties['installtype']))
        try:
            self.run_shell_command('npm',
                                   args=args,
                                   _cwd=self.app.get_source_path())
        except ShellCommandError:
            self.get_logger().command_error(
                'npm install {package} (properties: {properties!r}) FAILED!'.format(
                    package=package, properties=properties))
            raise SystemExit()

    def run_packagejson_script(self, script, args=None):
        args = args or []
        self.run_shell_command('npm',
                               args=['run', script] + args,
                               _cwd=self.app.get_source_path())

    def link_package(self, packagename):
        self.run_shell_command('npm',
                               args=['npm', 'link', packagename],
                               _cwd=self.app.get_source_path())

    def unlink_package(self, packagename):
        self.run_shell_command('npm',
                               args=['npm', 'unlink', packagename],
                               _cwd=self.app.get_source_path())
