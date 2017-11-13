import argparse
import logging
import os
import re
import sys

from pozetroncli.commands import CommandError
from . import commands
from .log import configure_logging
from .utils import random_sha256


def parse_module_name(s):
    if not re.match(r'^[0-9a-zA-Z_]+(?:/[0-9a-zA-Z_]+)*(?:\.m?py)?$', s):
        raise argparse.ArgumentTypeError('Enter a valid Python module name.')
    return s


def parse_package_name(s):
    if not re.match(r'^[a-zA-Z][0-9a-zA-Z_]*(?:[.-][0-9a-zA-Z_]+)*$', s):
        raise argparse.ArgumentTypeError('Enter a valid Python package name.')
    return s


def parse_hmac_key(s):
    if not re.match(r'^[0-9a-f]{64}$', s):
        raise argparse.ArgumentTypeError('Enter a valid hash (64 characters).\nMay we suggest: {}'
                                         .format(random_sha256()))
    return s


class Subparser(argparse.ArgumentParser):
    """Custom ArgumentParser to avoid copypaste."""

    def __init__(self, *args, **kwargs):
        super(Subparser, self).__init__(*args, **kwargs)
        # {func_arg: args.var}
        self.__func_args = {}

    def parse_device_email(self, device_id):
        if device_id.find('@') is -1:
            return device_id
        else:
            return device_id.split('@')[0]

    def add_filename(self):
        self.add_argument('-f', '--filename', required=True,
                          help='Script file name')
        self.__func_args['filename'] = 'filename'

    def add_dir(self):
        self.add_argument('-d', '--dir', required=True,
                          help='Package directory')
        self.__func_args['dirname'] = 'dir'

    def add_module(self):
        self.add_argument('-m', '--module', required=True,
                          type=parse_module_name,
                          help='Target module name (without ".py")')
        self.__func_args['module'] = 'module'

    def add_script_id(self):
        self.add_argument('-s', '--script', required=True,
                          help='Script ID (must have previously been uploaded to the cloud)')
        self.__func_args['script_id'] = 'script'

    def add_package_id(self):
        self.add_argument('-p', '--package', required=True,
                          help='Package ID (must have previously been uploaded to the cloud)')
        self.__func_args['package_id'] = 'package'

    def add_package_name(self):
        self.add_argument('-p', '--package', required=True,
                          type=parse_package_name,
                          help='Package name')
        self.__func_args['package_name'] = 'package'

    def add_ignore_data_files(self):
        self.add_argument('--ignore-data-files', action='store_true',
                          help='Ignore files other than *.py|*.mpy')
        self.__func_args['ignore_data_files'] = 'ignore_data_files'

    def add_function_id(self):
        self.add_argument('-fn', '--function', required=True,
                          help='Function ID (must have previously been created)')
        self.__func_args['function_id'] = 'function'

    def add_device_id(self):
        self.add_argument('-d', '--device', required=True, type=self.parse_device_email,
                          help='Device ID (must be already provisioned)')
        self.__func_args['device_id'] = 'device'

    def add_hmac_key(self):
        self.add_argument('-k', '--key', required=True,
                          type=parse_hmac_key,
                          help='HMAC key (your device\'s unique secret key)')
        self.__func_args['hmac_key'] = 'key'

    def add_code(self):
        self.add_argument('code',
                          help='Code to claim the device.')
        self.__func_args['code'] = 'code'

    def add_timestamp(self):
        self.add_argument('-ts', '--timestamp',
                          help='Timestamp (UNIX time)')
        self.__func_args['timestamp'] = 'timestamp'

    def add_enable_disable(self):
        self.add_argument('enable',
                          choices=('enable', 'disable'),
                          type=lambda x: x.lower(),
                          nargs='?',
                          help='Enable or disable logging')
        self.__func_args['enable'] = 'enable'

    def add_log_mode(self):
        self.add_argument('mode',
                          choices=('file', 'memory'),
                          type=lambda x: x.lower(),
                          nargs='?',
                          help='Where device should store logs before sending')
        self.__func_args['mode'] = 'mode'

    def add_firmware_device_type(self):
        self.add_argument('device-type',
                          choices=('esp8266', ),
                          type=lambda x: x.lower(),
                          nargs='?',
                          default='esp8266',
                          help='The supported device type')
        self.__func_args['device_type'] = 'device-type'

    def add_log_file_size(self):
        file_size_min = 1
        file_size_max = 0x100000

        def file_size(value):
            value = int(value)
            if not (file_size_min <= value <= file_size_max):
                raise argparse.ArgumentTypeError('file_size must be between {} and {}'
                                                 .format(file_size_min, file_size_max))
            return value

        self.add_argument('file_size',
                          type=file_size,
                          nargs='?',
                          help='Log file size on a device')
        self.__func_args['file_size'] = 'file_size'

    def add_hash(self):
        self.add_argument('hash',
                          help='Hash (64 characters)')
        self.__func_args['hash'] = 'hash'

    def add_tag(self):
        self.add_argument('tag',
                          help='Tag as "name" or "name:version". '
                               'Both name and version consist of alphanumeric characters '
                               'and separators (underscore, dash, period).')
        self.__func_args['tag'] = 'tag'

    def add_timezone(self):
        self.add_argument('timezone',
                          nargs='?',
                          default='local',
                          help='Timezone name. '
                               'Examples: local, UTC, US/Pacific, New_York.')
        self.__func_args['tz_name'] = 'timezone'

    def set_func(self, func):
        self.set_defaults(func=func, func_args=list(self.__func_args.items()))


def _parse_args(argv):
    """Returns argparse result."""
    parser = argparse.ArgumentParser(description='Pozetron command-line interface')
    parser.add_argument('-D', '--debug', action='store_true',
                        help='Enable debug mode for verbose logging')

    subparsers = parser.add_subparsers(dest='command', parser_class=Subparser)
    subparsers.required = True

    # Scripts
    script = subparsers.add_parser('script',
                                   description='Commands to manage scripts').add_subparsers()
    add_parser = script.add_parser

    sub = add_parser('upload',
                     description='Upload Python script to the cloud and print the script ID. '
                                 'After uploading, you can deploy the script to one or more of '
                                 'your devices using "poze.py deploy".')
    sub.add_filename()
    sub.add_module()
    sub.set_func(commands.upload)

    sub = add_parser('list',
                     description='Print the script ID of all of your scripts in the cloud.')
    sub.set_func(commands.list_scripts)

    sub = add_parser('rm',
                     description='Remove the script. This operation does not affect '
                                 'the devices with the script already deployed.')
    sub.add_script_id()
    sub.set_func(commands.rm_script)

    sub = add_parser('deploy', description='Deploy the script to the device.')
    sub.add_script_id()
    sub.add_device_id()
    sub.set_func(commands.deploy)

    sub = add_parser('undeploy', description='Undeploy the script from the device.')
    sub.add_script_id()
    sub.add_device_id()
    sub.set_func(commands.undeploy)

    sub = add_parser('list-deployed',
                     description='Print deployed script IDs for the device.')
    sub.add_device_id()
    sub.set_func(commands.list_deployed)

    # Packages
    package = subparsers.add_parser('package',
                                   description='Commands to manage packages').add_subparsers()
    add_parser = package.add_parser

    sub = add_parser('upload',
                     description='Upload Python package to the cloud and print the package ID. '
                                 'After uploading, you can deploy the package to one or more of '
                                 'your devices using "poze.py deploy-package".')
    sub.add_dir()
    sub.add_package_name()
    sub.add_ignore_data_files()
    sub.set_func(commands.upload_package)

    sub = add_parser('list',
                     description='Print the package ID of all of your packages in the cloud.')
    sub.set_func(commands.list_packages)

    sub = add_parser('describe', description='Print details of the given package.')
    sub.add_package_id()
    sub.set_func(commands.describe_package)

    sub = add_parser('rm', description='Remove the package. This operation does not '
                                               'affect the devices with the script already '
                                               'deployed.')
    sub.add_package_id()
    sub.set_func(commands.rm_package)

    sub = add_parser('deploy', description='Deploy the package to the device.')
    sub.add_package_id()
    sub.add_device_id()
    sub.set_func(commands.deploy_package)

    sub = add_parser('undeploy', description='Undeploy the package from the device.')
    sub.add_package_id()
    sub.add_device_id()
    sub.set_func(commands.undeploy_package)

    sub = add_parser('list-deployed',
                     description='Print deployed package IDs for the device.')
    sub.add_device_id()
    sub.set_func(commands.list_deployed_packages)

    # Device
    device = subparsers.add_parser('device',
                                    description='Commands to manage devices').add_subparsers()
    add_parser = device.add_parser

    sub = add_parser('provision',
                     description='Provision a new device with the given secret key, '
                                 'and the print new device ID (the part before the @) '
                                 'as well as the keyId. After provisioning, you can '
                                 'deploy scripts to the device using "poze.py deploy".')
    sub.add_hmac_key()
    sub.set_func(commands.provision)

    sub = add_parser('claim',
                     description='Claim a pre-provisioned device using a code. '
                                 'Result is the same as regular provision.')
    sub.add_code()
    sub.set_func(commands.claim)

    sub = add_parser('list', description='Print a list of provisioned devices.')
    sub.set_func(commands.list_devices)

    sub = add_parser('deprovision', description='Remove the device from the cloud.')
    sub.add_device_id()
    sub.set_func(commands.deprovision)

    sub = add_parser('reboot',
                     description='Send a reboot command to the device. '
                                 'Note: the actual reboot will happen next time '
                                 'the device checks in.')
    sub.add_device_id()
    sub.set_func(commands.reboot)

    sub = add_parser('forget-network',
                     description='Tell the device to forget the network settings. '
                                 'This will take effect on the next reboot of the device.')
    sub.add_device_id()
    sub.set_func(commands.forget_network)

    sub = add_parser('last-seen',
                     description='Print last-seen time of the device.')
    sub.add_timezone()
    sub.add_device_id()
    sub.set_func(commands.last_seen)

    sub = add_parser('log-mode',
                     description='Enable or disable logging on the device.')
    sub.add_device_id()
    sub.add_enable_disable()
    sub.add_log_mode()
    sub.add_log_file_size()
    sub.set_func(commands.log_mode)

    sub = add_parser('logs',
                     description='Print logs from the device, starting from a given timestamp.')
    sub.add_device_id()
    sub.add_timestamp()
    sub.set_func(commands.logs)

    sub = add_parser('firmware',
                     description='Download custom firmware for the device.')
    sub.add_device_id()
    sub.add_firmware_device_type()
    sub.set_func(commands.download_firmware)

    # Functions
    function = subparsers.add_parser('function',
                                     description='Commands to manage devices').add_subparsers()
    add_parser = function.add_parser

    sub = add_parser('provision',
                     description='Provision a new function.')
    sub.add_script_id()
    sub.set_func(commands.provision_function)

    sub = add_parser('deprovision',
                     description='Remove the function.')
    sub.add_function_id()
    sub.set_func(commands.deprovision_function)

    sub = add_parser('deploy',
                     description='Deploy the function to the device.')
    sub.add_function_id()
    sub.add_device_id()
    sub.set_func(commands.deploy_function)

    sub = add_parser('undeploy',
                     description='Undeploy the function from the device.')
    sub.add_function_id()
    sub.add_device_id()
    sub.set_func(commands.undeploy_function)

    # Tags
    tag = subparsers.add_parser('tag',
                                description='Commands to manage tags').add_subparsers()
    add_parser = tag.add_parser
    sub = add_parser('add',
                     description='Add a human-readable tag for a specific hash.')
    sub.add_hash()
    sub.add_tag()
    sub.set_func(commands.add_tag)

    sub = add_parser('rm',
                     description='Remove a tag.')
    sub.add_tag()
    sub.set_func(commands.remove_tag)

    if len(argv) == 0:
        parser.print_help()
        sys.exit(2)
    else:
        return parser.parse_args(argv)


def main(argv):
    """Main function. Returns system exit code."""
    args = _parse_args(argv)
    configure_logging(verbose=args.debug)
    logger = logging.getLogger('brief')
    server = os.getenv('POZETRON_SERVER')
    if server:
        commands.SERVER = server
    logger.debug('Pozetron server: {}'.format(commands.SERVER))
    try:
        func_args = {x: getattr(args, y) for x, y in args.func_args}
        args.func(**func_args)
        return 0
    except CommandError as exception:
        logger.error(str(exception))
        return 1
    except Exception:
        logger.exception('Unexpected error')
        return 1
    except KeyboardInterrupt:
        logger.info('Ctrl+C was pressed')
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # pragma: nocover
