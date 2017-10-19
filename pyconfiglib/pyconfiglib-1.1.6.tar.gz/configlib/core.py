"""
Utility to manage a configuration fileand provide an easy way to modify it.

To use the configlib in your project, just create a file name `conf.py` awith the following code

    import configlib

    class Config(configlib.Config):
        __config_path__ = 'my/path/to/the/config/file.json

        # you can define all class attributes as you want
        # as long as they don't start and end with a bouble underscore
        foot_size = 52

        bald  = True
        # you can specify the type of the field. It will be auto detected if you don't
        __bald_type__ = bool
        # you can also provide hint to enhance user experience
        __bald_hint__ = "Are you bald ?"

        # and you can not define any function (except super methods)
        name = "Archibald"

        # if a name starts with 'path_' or ends with '_path' there will be autocompletion
        # when the user wants to update it
        path_to_install = ''
        # OR you can just tell the type
        __path_to_install_type__ = configlib.path

        All basic types will be preserved even after save and loading them
        favourite_color = (230, 120, 32)

    if __name__ == '__main__':
        # with that the user will be able to easily edit the config by running `python config.py`
        configlib.update_config(Config)

    Then in your main code you can get the config with

    import config
    myconfig = config.Config()


Made with love by ddorn (https://github.com/ddorn/)
"""

import inspect
import json
import logging
import os
from typing import Tuple

import click

from .log import setup_logging
from .prompting import prompt_file
from . import conftypes

setup_logging(35)
logging.info('START')

try:
    import pygments
    from pygments.lexers import JsonLexer
    from pygments.formatters import TerminalFormatter
except ImportError:
    pygments = "You can install pygments with `pip install pygments` and have the output colored !"
    JsonLexer = None  # type: type
    TerminalFormatter = None  # type: type
    logging.debug('Pygment not installed')


TYPE_TO_CLICK_TYPE = {
    int: click.INT,
    float: click.FLOAT,
    str: click.STRING,
    bool: click.BOOL
}


# ✓
def is_config_field(attr: str):
    """Every string which doesn't start and end with '__' is considered to be a valid usable configuration field."""
    return not (attr.startswith('__') and attr.endswith('__'))


# ✓
def prompt_update_all(config: 'Config'):
    """Prompt each field of the configration to the user."""

    click.echo()
    click.echo('Welcome !')
    click.echo('Press enter to keep the defaults or enter a new value to update the configuration.')
    click.echo('Press Ctrl+C at any time to quit and save')
    click.echo()

    for field in config:

        type_ = config.__type__(field)
        hint = config.__hint__(field) + ' ({})'.format(type_.__name__)

        if isinstance(type_, conftypes.SubConfigType):
            continue

        # we prompt the paths through prompt_file and not click
        if type_ is conftypes.path:
            config[field] = prompt_file(hint, default=config[field])
            continue

        if isinstance(type_, conftypes.ConfigType):
            # config[field] is always real data, but we want to show something that is the closest
            # possible to what the user needs to enter
            # thus, we show what we would store in the json
            default = type_.save(config[field])
        else:
            default = config[field]

        # a too long hint is awfull
        if len(str(default)) > 14:
            default = str(default)[:10] + '...'

        # ask untill we have the right type
        value = click.prompt(hint, default=default, type=type_)

        # click doesnt convert() the default if nothing is entered, so it wont be valid
        # however we don't care because default means that we don't have to update
        if value == default:
            logging.debug('same value and default, skipping set. %r == %r', value, default)
            continue

        config[field] = value


# ✓
class Config(object):
    # the path where the configuration is stored. The directory must exist
    __config_path__ = 'config.json'

    # ✓
    def __init__(self):
        self.__load__()

    # ✓
    def __init_subclass__(cls, **kwargs):

        # this is called every times a subclass of Config is made.
        # Here we add all the missing types so the type of the default can not change
        # when there is not __field_type__.

        for field in list(cls.__dict__):
            if not is_config_field(field):
                continue

            field_type_name = '__{field}_type__'.format(field=field)

            # if it is an implicit type
            if not hasattr(cls, field_type_name):
                # we add the type of the default
                default = getattr(cls, field)
                if isinstance(default, SubConfig):
                    setattr(cls, field_type_name, conftypes.SubConfigType(type(default)))
                else:
                    setattr(cls, field_type_name, type(default))
                    logging.debug('In %s the field %s has now type %s because the default is %r', cls, field,
                                  type(default), default)

    # ✓
    def __iter__(self):
        """Iterate over the fields, sorted."""

        # the fields are all class atributes,
        # so they are accessible from everywhere
        keys = sorted(type(self).__dict__)
        for key in keys:
            if is_config_field(key):
                yield key

    def __contains__(self, item: str):
        # if there is a dot in item, it is a field of a subconfig
        if '.' in item:
            item, _, sub_item = item.partition('.')
            if hasattr(self, item) and isinstance(self[item], SubConfig):
                return sub_item in self[item]
            else:
                return False
        return is_config_field(item) and hasattr(self, item)

    def __load__(self):
        try:
            with open(self.__config_path__, 'r', encoding='utf-8') as f:
                file = f.read()
            logging.info('Read %d chars from %s', len(file), self.__config_path__)
        except FileNotFoundError:
            # if no config was ever created, it's time to make one
            file = '{}'
            logging.info('Config file not found, creating empty one')

        conf = json.loads(file)  # type: dict

        self.__update__(conf)

    # ✓
    def __save__(self):
        """Save the config to __config_path__ in a json format."""

        jsonstr = json.dumps(self.__get_json_dict__(), indent=4, sort_keys=True)

        logging.info('saving %d chars at %s', len(jsonstr), self.__config_path__)
        with open(self.__config_path__, 'w', encoding='utf-8') as f:
            f.write(jsonstr)

    def __get_json_dict__(self):
        json_dict = {}
        for attr in self:
            # we want to save only the fields
            if is_config_field(attr):

                supposed_type = self.__type__(attr)
                # but we may need to convert the to something json knows
                # if the type is a custom type
                if isinstance(supposed_type, conftypes.ConfigType):
                    json_dict[attr] = supposed_type.save(self[attr])
                else:
                    json_dict[attr] = self[attr]

        return json_dict

    # ✓
    def __len__(self):
        # we can't do len(list(self)) because list uses len when it can, causing recurtion of the death
        return sum(1 for _ in self)

    # ✓
    def __setitem__(self, field, value):
        """
        Sets a field to a given value if it is a correct type.

        :param field: needs to be an existing field
        :raise ValueError: when the value is not valid.
        """

        # if there is a dot in the name, we want to set an field of a subconfig
        if '.' in field:
            field, _, subfield = field.partition('.')
            logging.debug('setting subitem %s in %s', subfield, field)
            self[field][subfield] = value
            return

        supposed_type = self.__type__(field)

        logging.debug('SETITEM %s to %r supposed type: %s', field, value, supposed_type)

        if conftypes.is_valid(value, supposed_type):
            # everything is correct, we assign is directly
            self.__setattr__(field, value)
            logging.debug('valid')


        elif isinstance(supposed_type, conftypes.ConfigType):
            # we may need to convert it
            logging.debug('try to convert the value through ConfigType')
            try:
                value = supposed_type.load(value)
                self.__setattr__(field, value)
            except Exception:
                logging.warning('fail loading %r of type %s but supposed %s', value, type(value), supposed_type)
                raise ValueError('fail loading %r of type %s but supposed %s' % (value, type(value), supposed_type))

        elif supposed_type in TYPE_TO_CLICK_TYPE:
            try:
                logging.debug('try to convert the value throught click.ParamType')
                value = TYPE_TO_CLICK_TYPE[supposed_type](value)
                self.__setattr__(field, value)
            except Exception:
                logging.warning('fail loading %r of type %s but supposed %s', value, type(value), supposed_type)
                raise ValueError('fail loading %s of type %s but supposed %s' % (value, type(value), supposed_type))
        else:
            # it is just not good
            logging.warning('fail loading %r of type %s but supposed %s', value, type(value), supposed_type)
            raise ValueError('fail loading %s of type %s but supposed %s' % (value, type(value), supposed_type))

    # ✓
    def __getitem__(self, item: str):
        # proxy to getattribute to have be symetrical to __setitem__
        if '.' in item:
            item, _, sub = item.partition('.')
            return self[item][sub]
        return self.__getattribute__(item)

    # ✓
    def __enter__(self):
        """The context manager patern ensures that the config will be saved."""
        return self

    # ✓
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__save__()
        click.echo('\nSaved!')

    # ✓
    def __print_list__(self, prefix=''):
        """Print all the availaible fields with their order and type."""

        if not prefix:
            click.echo("The following fields are available: ")

        # we list the fields
        for field in self:
            if isinstance(self[field], SubConfig):
                continue

            # we print the supposed type
            type_ = click.style(self.__type__(field).__name__, fg='yellow')
            text = '{field} ({type})  '.format(field=field, type=type_)

            if self.__hint__(field) != field:
                # 51 and not 42 because of the size of the ansii escape sequence
                click.echo('{pre} - {text:.<51}  {hint}'.format(pre=prefix, text=text, hint=self.__hint__(field)))
            else:
                click.echo('{pre} - {text}'.format(pre=prefix, text=text))

        # and then the subconfigs
        for field in self:
            if not isinstance(self[field], SubConfig):
                continue

            if self.__hint__(field) != field:
                click.echo('{pre} - {field:.<42}  {hint}'.format(pre=prefix, field=field + ':  ', hint=self.__hint__(field)))
            else:
                click.echo('{pre} - {field}:'.format(pre=prefix, field=field))
            self[field].__print_list__(prefix + '    ')
    # ✓
    def __show__(self):
        """Print the json that stores the data with colors."""

        try:
            with open(self.__config_path__, 'r', encoding='utf-8') as f:
                file = f.read()
        except FileNotFoundError:
            click.echo("You don't have any configuration.")
            return

        file = json.dumps(json.loads(file), indent=4, sort_keys=True)

        # I've set pygments to an help str when there is an import error
        if isinstance(pygments, str):
            click.secho(pygments, fg='yellow')
        else:
            # add ansii coloring
            file = pygments.highlight(file, JsonLexer(), TerminalFormatter())

        click.echo()
        click.echo(file)

    # ✓
    def __update__(self, dct):
        """
        Update all the fields with the key/values in the dict.

        When the type is wrong, a warning is printed and the field is not updated.
        Return the succes of settin ALL fields of the dict.
        """

        one_field_is_with_a_bad_type = False

        for field, value in dct.items():

            # we update only the fields in the conf so if someone added fields in the json,
            # they won't interfere with the already defines attributes...
            # For instance, we don't want to override __load__.

            if field not in self:
                logging.debug('field %s is not in the config', field)
                continue

            try:
                self[field] = value
            except ValueError:
                logging.debug('failed to set %s to %r but we ignore it', field, value)
                one_field_is_with_a_bad_type = True
                self.__warn__(value, field)

        if one_field_is_with_a_bad_type:
            click.echo("You can run `python {}` to update the configuration".format(
                os.path.relpath(inspect.getfile(self.__class__))))

        return one_field_is_with_a_bad_type

    # ✓
    def __warn__(self, value, field):
        """Show a colored message to say that the field is not of the right type."""

        click.echo('The field ', nl=False)
        click.secho(field, nl=False, fg='yellow')
        click.echo(' is a ', nl=False)
        click.secho(type(value).__name__, nl=False, fg='red')
        click.echo(' but should be ', nl=False)
        click.secho(self.__type__(field).__name__, nl=False, fg='green')
        click.echo('.')

    # ✓
    def __type__(self, field: str):
        """Get the type given by __field_type__"""
        if '.' in field:
            subconfigs, _, field = field.rpartition('.')
            return self['{subconfigs}.__{field}_type__'.format(subconfigs=subconfigs,
                                                               field=field)]
        return self['__{field}_type__'.format(field=field)]

    # ✓
    def __hint__(self, field):
        """Get the hint given by __field_hint__ or the field name if not defined."""
        return getattr(self, '__{field}_hint__'.format(field=field), field)


class SubConfig(Config):
    # noinspection PyMissingConstructor
    def __init__(self, dct=None):
        dct = dct or {}

        self.__update__(dct)


def update_config(config: type(Config)):
    """Command line function to update and the a config."""

    # we build the real click command inside the function, because it needs to be done
    # dynamically, depending on the config.

    # we ignore the type errors, keeping the the defaults if needed
    # everything will be updated anyway
    config = config()  # type: Config

    def print_list(ctx, param, value):
        # they do like that in the doc (http://click.pocoo.org/6/options/#callbacks-and-eager-options)
        # so I do the same... but I don't now why.
        # the only goal is to call __print_list__()
        if not value or ctx.resilient_parsing:
            return param

        config.__print_list__()

        ctx.exit()

    def show_conf(ctx, param, value):
        # see print_list
        if not value or ctx.resilient_parsing:
            return param

        config.__show__()

        ctx.exit()

    def clean(ctx, param, value):
        # see print_list
        if not value or ctx.resilient_parsing:
            return param

        config.__save__()
        click.echo('Cleaned !')

        ctx.exit()

    @click.command(context_settings={'ignore_unknown_options': True})
    @click.option('-c', '--clean', is_eager=True, is_flag=True, expose_value=False, callback=clean,
                  help='Clean the file where the configutation is stored.')
    @click.option('-l', '--list', is_eager=True, is_flag=True, expose_value=False, callback=print_list,
                  help='List the availaible configuration fields.')
    @click.option('-s', '--show', is_eager=True, is_flag=True, expose_value=False, callback=show_conf,
                  help='View the configuration.')
    @click.argument('fields-to-set', nargs=-1, type=click.UNPROCESSED)
    def command(fields_to_set: 'Tuple[str]'):
        """
        I manage your configuration.

        If you call me with no argument, you will be able to set each field
        in an interactive prompt. I can show your configuration with -s,
        list the available field with -l and set them by --name-of-field=whatever.
        """

        # with a context manager, the config is always saved at the end
        with config:

            if len(fields_to_set) == 1 and '=' not in fields_to_set[0]:
                # we want to update a part of the config
                sub = fields_to_set[0]
                if sub in config:
                    if isinstance(config[sub], SubConfig):
                        # the part is a subconfig
                        prompt_update_all(config[sub])
                    else:
                        # TODO: dynamic prompt for one field
                        raise click.BadParameter('%s is not a SubConfig of the configuration')

                else:
                    raise click.BadParameter('%s is not a field of the configuration')

            elif fields_to_set:
                dct = {}
                for field in fields_to_set:
                    field, _, value = field.partition('=')
                    dct[field] = value
                # save directly what is passed if something was passed whitout the interactive prompt
                config.__update__(dct)
            else:
                # or update all
                prompt_update_all(config)

    # this is the real function for the CLI
    logging.debug('start command')
    command()
    logging.debug('end command')


__all__ = ['Config', 'SubConfig', 'update_config']
