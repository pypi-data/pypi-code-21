from __future__ import absolute_import, division, print_function
import argparse
import os
from . import is_a

try:
    import hosts
    has_hosts = True
except ImportError:
    has_hosts = False


class BaseSettings(object):
    def __init__(self):
        super(BaseSettings, self).__init__()
        self._queued_args = []  # all the arg and kwargs are stored in a tuple

    def add_argument(self, arguments, action=None, nargs=None, const=None, default=None, type=None, choices=None, required=None, help=None, metavar=None, dest=None, commands=None, **kw):

        if action is not None:
            kw['action'] = action
        if nargs is not None:
            kw['nargs'] = nargs
        if const is not None:
            kw['const'] = const
        if default is not None:
            kw['default'] = default
        if type is not None:
            kw['type'] = type
        if choices is not None:
            kw['choices'] = choices
        if required is not None:
            kw['required'] = required
        if help is not None:
            kw['help'] = help
        if metavar is not None:
            kw['metavar'] = metavar
        if dest is not None:
            kw['dest'] = dest

        self._queue_arg(*arguments, **kw)

    # this method is used by all subclasses to add arguments into their own respective _queued_args structure, either a dict or a list
    def _queue_arg(self, *args, **kwargs):
        self._queued_args.append((args, kwargs))

    def int_argument(self, arguments, choices=None, default=None, required=None, help=None, metavar=None, dest=None, commands=None):
        self.add_argument(arguments, type=int, choices=choices, default=default,
                          required=required, help=help, metavar=metavar, dest=dest, commands=commands)

    def string_argument(self, arguments, default=None, required=None, help=None, metavar=None, dest=None, commands=None):
        self.add_argument(arguments, type=str, default=default,
                          required=required, help=help, metavar=metavar, dest=dest, commands=commands)

    def path_argument(self, arguments, default=None, required=None, help=None, metavar=None, dest=None, exists=True, commands=None):
        self.add_argument(arguments, type=lambda x: self._path(
            exists, x), default=default, required=required, help=help, metavar=metavar, dest=dest, commands=commands)

    def bool_argument(self, arguments, default=None, required=None, help=None, metavar=None, dest=None, commands=None):
        self.add_argument(arguments, type=self._bool, default=default,
                          required=required, help=help, metavar=metavar, dest=dest, commands=commands)

    def feature_argument(self, feature, default, required=None, help=None, metavar=None, commands=None):
        if default != True and default != False:
            err_str = "Default value for feature has to be a True or False value"
            if has_hosts:
                hosts.output.WriteError(err_str, show_stack=False)
            else:
                raise RuntimeError(err_str)

        self.add_argument(["--enable-{0}".format(feature)], action='store_true',
                          default=default, required=required, help=help, metavar=metavar, dest=feature, commands=commands)
        self.add_argument(["--disable-{0}".format(feature)], action='store_false',
                          default=default, required=required, help=help, metavar=metavar, dest=feature, commands=commands)

    # add option for mapping x -> y values
    def enum_argument(self, arguments, choices, default=None, required=None, help=None, metavar=None, dest=None, commands=None):
        self.add_argument(arguments, choices=choices, type=int, default=default,
                          required=required, help=help, metavar=metavar, dest=dest, commands=commands)

    def list_argument(self, arguments, nargs="*", choices=None, default=None, required=None, help=None, metavar=None, dest=None, commands=None):
        self.add_argument(arguments, action=extendAction, nargs=nargs, choices=choices,
                          type=str, default=default, required=required, help=help, metavar=metavar, dest=dest, commands=commands)

    def _bool(self, arg):
        opt_true_values = set(['y', 'yes', 'true', 't', '1', 'on', 'all'])
        opt_false_values = set(['n', 'no', 'false', 'f', '0', 'off', 'none'])

        tmp = arg.lower()
        if tmp in opt_true_values:
            return True
        elif tmp in opt_false_values:
            return False
        else:
            msg = 'Invalid value Boolean value : "{0}"\n Valid options are {0}'.format(arg,
                                                                                       opt_true_values | opt_false_values)
            raise argparse.ArgumentTypeError(msg)

    def _path(self, exists, arg):
        path = os.path.abspath(arg)
        if not os.path.exists(path) and exists:
            msg = '"{0}" is not a valid path'.format(path)
            raise argparse.ArgumentTypeError(msg)
        return path


class RestrictedBase(BaseSettings):
    def __init__(self):
        super(RestrictedBase, self).__init__()

    def int_argument(self, arguments, choices=None, default=None, required=None, help=None, metavar=None, dest=None):
        self.add_argument(arguments, type=int, choices=choices, default=default,
                          required=required, help=help, metavar=metavar, dest=dest)

    def string_argument(self, arguments, default=None, required=None, help=None, metavar=None, dest=None):
        self.add_argument(arguments, type=str, default=default,
                          required=required, help=help, metavar=metavar, dest=dest)

    def path_argument(self, arguments, default=None, required=None, help=None, metavar=None, dest=None, exists=True):
        self.add_argument(arguments, type=lambda x: self._path(
            exists, x), default=default, required=required, help=help, metavar=metavar, dest=dest)

    def bool_argument(self, arguments, default=None, required=None, help=None, metavar=None, dest=None):
        self.add_argument(arguments, type=self._bool, default=default,
                          required=required, help=help, metavar=metavar, dest=dest)

    def feature_argument(self, feature, default, required=None, help=None, metavar=None):
        if default != True and default != False:
            err_str = "Default value for feature has to be a True or False value"
            if has_hosts:
                hosts.output.WriteError(err_str, show_stack=False)
            else:
                raise RuntimeError(err_str)

        self.add_argument(["--enable-{0}".format(feature)], action='store_true',
                          default=default, required=required, help=help, metavar=metavar, dest=feature)
        self.add_argument(["--disable-{0}".format(feature)], action='store_false',
                          default=default, required=required, help=help, metavar=metavar, dest=feature)

    # add option for mapping x -> y values
    def enum_argument(self, arguments, choices, default=None, required=None, help=None, metavar=None, dest=None):
        self.add_argument(arguments, choices=choices, type=int, default=default,
                          required=required, help=help, metavar=metavar, dest=dest)

    def list_argument(self, arguments, nargs="*", choices=None, default=None, required=None, help=None, metavar=None, dest=None):
        self.add_argument(arguments, action=extendAction, nargs=nargs, choices=choices,
                          type=str, default=default, required=required, help=help, metavar=metavar, dest=dest)


class Settings(BaseSettings):
    def __init__(self):
        super(Settings, self).__init__()

        self.__commands = {}           # "cmd name" : Command object
        self._queued_args = {'*': []}  # "cmd name" : [(args, kwargs)]
        self.__queued_groups = []
        self.__parser = None    # made in setup
        self.__subparser = None  # made in setup, if there are available commands
        self.__arguments = None
        self.__unknowns = None

    @property
    def arguments(self):
        return self.__arguments

    @property
    def unknowns(self):
        return self.__unknowns

    @property
    def parser(self):
        return self.__parser

    def add_command(self, name, *args, **kwargs):
        self.__commands[name] = Command(name, *args, **kwargs)
        return self.__commands[name]

    def _queue_arg(self, *args, **kwargs):
        if 'commands' in kwargs:    # if we are adding to specific commands and not globally
            cmds = kwargs['commands']
            del kwargs['commands']

            for cmd in cmds:
                try:
                    self._queued_args[cmd].append((args, kwargs))
                except KeyError:
                    self._queued_args[cmd] = [(args, kwargs)]
        else:   # adding globally to every command available
            self._queued_args['*'].append((args, kwargs))

    def add_argument_group(self, title=None, description=None):
        group = Group(self.__commands, title=title, description=description)
        self.__queued_groups.append(group)

        return group

    # calling function (partial_parse or final_parse) will init the main parser
    def _setup(self, full_parse=False):
        if self.__commands and full_parse:  # if we have various different commands
            self.__subparser = self.__parser.add_subparsers(dest='subcommand')

            # first tell commands to add their arguments, then commands' private groups and global commands
            for cmd in self.__commands:
                # initializes to the global arguments
                cmds = self._queued_args['*']

                # check and add any arguments just for this command
                if cmd in self._queued_args:
                    cmds.extend(self._queued_args[cmd])

                self.__commands[cmd]._setup(self.__subparser, cmds)
        else:   # if we only have 1 main parser
            for args, kwargs in self._queued_args['*']:
                self.__parser.add_argument(*args, **kwargs)

        # last step: add global groups
        for group in self.__queued_groups:
            group._setup(self.__parser, full_parse)

    def partial_parse(self):
        self.__parser = argparse.ArgumentParser(add_help=False)
        self._setup()

        self.__arguments, self.__unknowns = self.__parser.parse_known_args()

    def final_parse(self):
        self.__parser = argparse.ArgumentParser()
        self._setup(True)

        self.__arguments = self.__parser.parse_args()

    def parse_known_args(self):
        self.partial_parse()

        return (self.__arguments, self.__unknowns)

    def get_argument(self, name):
        return self.__arguments.get(name)


class Command(RestrictedBase):
    def __init__(self, name, *args, **kwargs):
        super(Command, self).__init__()

        self.__name = name
        self.__args = args
        self.__kwargs = kwargs
        self.__queued_groups = []
        self.__parser = None    # initalized in the setup step

    @property
    def name(self):
        return self.__name

    @property
    def parser(self):
        return self.__parser

    def add_argument_group(self, title=None, description=None):
        group = RestrictedGroup(title, description)
        self.__queued_groups.append(group)

        return group

    def _setup(self, subparser, cmds):
        self.__parser = subparser.add_parser(
            self.__name, *self.__args, **self.__kwargs)

        # first we add our own arguments
        for args, kwargs in self._queued_args:
            self.__parser.add_argument(*args, **kwargs)

        # then we add any supplied arguments from Settings (global or specific)
        if cmds:
            for args, kwargs in cmds:
                self.__parser.add_argument(*args, **kwargs)

        # lastly we add the arguments in the private groups
        for group in self.__queued_groups:
            group._setup(self.__parser)


class Group(BaseSettings):
    def __init__(self, commands, title=None, description=None):
        super(Group, self).__init__()

        self.__title = title
        self.__description = description
        self._queued_args = {'*': []}  # cmd: [args] 'run': [(a, b), (c,d)]
        self.__commands = commands

    def _queue_arg(self, *args, **kwargs):
        if 'commands' in kwargs:    # if we are adding to specific commands and not globally in the group
            cmds = kwargs['commands']
            del kwargs['commands']

            for cmd in cmds:
                try:
                    self._queued_args[cmd].append((args, kwargs))
                except KeyError:
                    self._queued_args[cmd] = [(args, kwargs)]
        else:   # adding globally to all the commands
            self._queued_args['*'].append((args, kwargs))

    # parser argument is for the 1 main parser case, where we only add the global arguments
    def _setup(self, parser=None, full_parse=False):
        if self.__commands and full_parse:  # like in Settings, differentiate between 1 main parser and having subparsers
            for cmd_name in self.__commands:
                cmd = self.__commands[cmd_name]  # get the command object

                # make a complete list of all arguments for this particular command then add them
                arg_list = self._queued_args['*']

                if cmd_name in self._queued_args:
                    arg_list.extend(self._queued_args[cmd_name])

                grp = _get_group(cmd.parser, self.__title, self.__description)

                for args, kwargs in arg_list:
                    grp.add_argument(*args, **kwargs)
        else:
            grp = _get_group(parser, self.__title, self.__description)

            for args, kwargs in self._queued_args['*']:
                grp.add_argument(*args, **kwargs)


class RestrictedGroup(RestrictedBase):
    def __init__(self, title=None, description=None):
        super(RestrictedGroup, self).__init__()

        self.__title = title
        self.__description = description

    def _setup(self, parser):
        group = _get_group(parser, self.__title, self.__description)

        for args, kwargs in self._queued_args:
            group.add_argument(*args, **kwargs)


# Checks if an argument group already exists, and returns a new one if it doesn't
def _get_group(parser, title, description):
    for arg_grp in parser._action_groups:
        if arg_grp.title == title and arg_grp.description == description:
            return arg_grp

    return parser.add_argument_group(title, description)


def JobValues(arg):
    try:
        j = int(arg)
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid int value {0}".format(arg))
    if j == 0:
        j = 1
    if j < 0:
        msg = 'Must be a postive value'.format(j)
        raise argparse.ArgumentTypeError(msg)
    return j


class extendAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):

        if is_a.Int(nargs) and nargs <= 1:
            raise ValueError(
                'Invalid value for nargs:\n must be "+" or "*" or a number greater than 1')
        elif is_a.String(nargs) and nargs not in ("+", "*"):
            raise ValueError(
                'Invalid value for nargs:\n must be "+" or "*" or a number greater than 1')
        elif not is_a.String(nargs) and not is_a.Int(nargs):
            raise ValueError(
                'nargs for extend actions must be a string or int type')

        super(extendAction, self).__init__(option_strings=option_strings,
                                           dest=dest,
                                           nargs=nargs,
                                           const=const,
                                           default=default,
                                           type=type,
                                           choices=choices,
                                           required=required,
                                           help=help,
                                           metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = []
        for i in values:
            if i[-1] == ',':
                i = i[:-1]
            i = i.split(",")
            items.extend(i)
        setattr(namespace, self.dest, items)
