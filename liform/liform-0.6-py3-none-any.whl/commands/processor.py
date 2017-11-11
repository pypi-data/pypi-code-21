class TextFilter(object):
    def __init__(self, text):
        self.__text = text

    def __call__(self, value):
        return value == self.__text


class RegexFilter(object):
    def __init__(self, pattern):
        from re import compile as re_compile

        self.__pattern = re_compile(pattern)

    def __call__(self, value):
        return not self.__pattern.search(value) is None


class CommandProcessor(object):
    def __init_args(self):
        from argparse import ArgumentParser
        from argparse import RawTextHelpFormatter
        from collections import OrderedDict

        parser = ArgumentParser(description='Orchestrate Linode servers.', formatter_class=RawTextHelpFormatter)

        parser.add_argument(
            '-a', '--action', dest='actions', action='append', required=True,
            choices=['display', 'prepare', 'refresh', 'destroy', 'degrade'],
            metavar='display|prepare|refresh|destroy|degrade',
            help='Action to perform.')
        parser.add_argument(
            '-c', '--column', dest='columns', action='append', required=False, nargs='+',
            choices=['id', 'ipv4', 'ipv6', 'name', 'path', 'state', 'type'],
            metavar='id|ipv4|ipv6|name|path|state|type',
            help='Output columns.')
        parser.add_argument(
            '-f', '--format', dest='format', action='store', default='text', required=False,
            choices=['text', 'json', 'csv'],
            metavar='text|json|csv',
            help='Output format.')
        parser.add_argument(
            '-p', '--path', dest='paths', action='append', required=False,
            metavar='test',
            help='''Path of resource or resource path pattern if starts with ~ symbol.
If specified multiple times resources with match any of path or pattern will be selected.''')
        parser.add_argument(
            '-m', '--module', dest='module', action='store', required=True,
            metavar='module.xml',
            help='Path to file with module.')
        parser.add_argument(
            '-s', '--setting', dest='settings', action='append', required=False,
            metavar='name=value',
            help='Name and value of setting\r\nOr "@" followed by path of ini style file.')
        parser.add_argument(
            '-v', '--variable', dest='variables', action='append', required=False,
            metavar='name=value',
            help='Name and value of variable\r\nOr "@" followed by path of ini style file.')

        self.__args = parser.parse_args()
        self.__columns = OrderedDict()

        if self.__args.columns is None:
            self.__args.columns = [['type', 'name', 'id', 'ipv4', 'state']]

        for columns in self.__args.columns:
            for column in columns:
                if column == 'id':
                    self.__columns['id'] = 'ID'
                elif column == 'ipv4':
                    self.__columns['ipv4'] = 'IPv4'
                elif column == 'ipv6':
                    self.__columns['ipv6'] = 'IPv6'
                elif column == 'name':
                    self.__columns['name'] = 'Name'
                elif column == 'path':
                    self.__columns['path'] = 'Path'
                elif column == 'state':
                    self.__columns['state_text'] = 'State'
                elif column == 'type':
                    self.__columns['type'] = 'Type'

    def __init_resource_handlers(self):
        from ..handlers.dnf import InstallHandler as DnfInstallHandler
        from ..handlers.dnf import RemoveHandler as DnfRemoveHandler
        from ..handlers.linode import ServerHandler as LinodeServerHandler
        from ..handlers.linode import DiskHandler as LinodeDiskHandler
        from ..handlers.linode import VolumeHandler as LinodeVolumeHandler
        from ..handlers.pip2 import InstallHandler as Pip2InstallHandler
        from ..handlers.pip2 import UninstallHandler as Pip2UninstallHandler
        from ..handlers.pip3 import InstallHandler as Pip3InstallHandler
        from ..handlers.pip3 import UninstallHandler as Pip3UninstallHandler
        from ..handlers.ssh import UploadHandler as SshUploadHandler
        from ..handlers.ssh import ExecuteHandler as SshExecuteHandler

        self.__resource_handlers = {
            '{linode}server': LinodeServerHandler,
            '{linode}disk': LinodeDiskHandler,
            '{linode}volume': LinodeVolumeHandler,
            '{ssh}upload': SshUploadHandler,
            '{ssh}execute': SshExecuteHandler,
            '{dnf}install': DnfInstallHandler,
            '{dnf}remove': DnfRemoveHandler,
            '{pip2}install': Pip2InstallHandler,
            '{pip2}uninstall': Pip2UninstallHandler,
            '{pip3}install': Pip3InstallHandler,
            '{pip3}uninstall': Pip3UninstallHandler,
        }

    def __init_settings(self):
        from ..resources.parsers import OptionParser

        setting_parser = OptionParser()

        for setting in self.__args.settings:
            setting_parser.add(setting)

        self.__settings = setting_parser.values

    def __init_variables(self):
        from ..resources.parsers import OptionParser

        variable_parser = OptionParser()

        for variable in self.__args.variables:
            variable_parser.add(variable)

        self.__variables = variable_parser.values

    def __init_state_database(self):
        from ..resources.state import StateDatabase

        self.__state_database = StateDatabase(self.__settings)

    def __init_module_processor(self):
        from ..resources.parsers import ModuleParser
        from ..resources.processors import ModuleProcessor

        self.__module_parser = ModuleParser(self.__resource_handlers, self.__variables)
        self.__module_parser.load_root_module(self.__args.module)

        self.__module_processor = ModuleProcessor(self.__resource_handlers)
        self.__module_processor.resolve_resources(self.__module_parser.resources)
        self.__module_processor.select_state(self.__state_database)
        self.__resources = self.__module_processor.resources

    def __init__resource_every(self, resource):
        resource._opted_in = True
        resource._child_opted_in = True

        for child in resource.children:
            self.__init__resource_every(child)

    def __init__resource_filter(self, resource):
        resource._opted_in = False
        resource._child_opted_in = False

        for filter in self.__resource_filters:
            if filter(resource.path):
                resource._opted_in = True
                break

        for child in resource.children:
            self.__init__resource_filter(child)
            resource._child_opted_in = resource._child_opted_in or child._opted_in

    def __init__resources(self):
        if self.__args.paths:
            self.__resource_filters = []

            for path in self.__args.paths:
                if path.startswith('~'):
                    self.__resource_filters.append(RegexFilter(path[1:]))
                else:
                    self.__resource_filters.append(TextFilter(path))

            for resource in self.__resources:
                self.__init__resource_filter(resource)
        else:
            for resource in self.__resources:
                self.__init__resource_every(resource)

    def __init__phases(self):
        self.__phases = self.__module_parser.phases

    def __init__(self):
        self.__init_args()
        self.__init_resource_handlers()
        self.__init_settings()
        self.__init_variables()
        self.__init_state_database()
        self.__init_module_processor()
        self.__init__resources()
        self.__init__phases()

    def __display(self):
        from .display import DisplayCsvCommand
        from .display import DisplayJsonCommand
        from .display import DisplayTextCommand

        if self.__args.format == 'text':
            command = DisplayTextCommand(self.__resources, self.__columns)
        elif self.__args.format == 'json':
            command = DisplayJsonCommand(self.__resources, self.__columns)
        elif self.__args.format == 'csv':
            command = DisplayCsvCommand(self.__resources, self.__columns)

        command.run()

    def __prepare(self):
        from .display import DisplayCsvCommand
        from .display import DisplayJsonCommand
        from .display import DisplayTextCommand

        error_resources = [resource for resource in self.__resources if not resource.state]

        if self.__args.format == 'text':
            command = DisplayTextCommand(error_resources, self.__columns)
        elif self.__args.format == 'json':
            command = DisplayJsonCommand(error_resources, self.__columns)
        elif self.__args.format == 'csv':
            command = DisplayCsvCommand(error_resources, self.__columns)

        command.run()

    def __refresh(self):
        from .handler import RefreshCommand

        command = RefreshCommand(self.__resources, self.__phases, self.__settings, self.__variables)
        command.run()

    def __destroy(self):
        from .handler import DestroyCommand

        command = DestroyCommand(self.__resources, self.__phases, self.__settings, self.__variables)
        command.run()

    def __degrade(self):
        from .degrade import DegradeCommand

        command = DegradeCommand(self.__resources)
        command.run()

    def run(self):
        for action in self.__args.actions:
            try:
                if action == 'display':
                    self.__display()
                elif action == 'prepare':
                    self.__prepare()
                elif action == 'refresh':
                    self.__refresh()
                elif action == 'destroy':
                    self.__destroy()
                elif action == 'degrade':
                    self.__degrade()
            finally:
                self.__module_processor.update_state(self.__state_database)
