# coding=utf-8
import os

import click

from mali_commands.utilities.os_utils import create_dir

try:
    # noinspection PyPep8Naming
    import ConfigParser as configparser
except ImportError:
    # noinspection PyUnresolvedReferences
    import configparser

_missing_link_config = 'missinglink.cfg'


default_api_host = 'https://missinglinkai.appspot.com'
default_host = 'https://missinglink.ai'
default_client_id = 'nbkyPAMoxj5tNzpP07vyrrsVZnhKYhMj'
default_auth0 = 'missinglink'


def default_missing_link_folder():
    return os.path.join(os.path.expanduser('~'), '.MissingLinkAI')


def default_config_file(config_prefix, filename):
    filename_with_prefix = '%s-%s' % (config_prefix, filename) if config_prefix else filename
    return os.path.join(default_missing_link_folder(), filename_with_prefix)


def find_first_file(config_prefix, filename):
    filename_with_prefix = '%s-%s' % (config_prefix, filename) if config_prefix else filename

    possible_paths = [os.getcwd(), default_missing_link_folder()]

    for possible_path in possible_paths:
        candidate_config_file = os.path.join(possible_path, filename_with_prefix)

        if os.path.isfile(candidate_config_file):
            return candidate_config_file

    return None


class Config(object):
    def __init__(self, config_prefix, config_file):
        self.config_file = config_file
        self.config_prefix = config_prefix

        if self.config_file:
            self.config_file_abs_path = os.path.abspath(config_file)
        else:
            self.config_file_abs_path = find_first_file(self.config_prefix, _missing_link_config)

        should_check_file_exists = config_prefix or config_file

        if should_check_file_exists and not os.path.exists(self.config_file_abs_path):
            click.echo('config file %s not found' % self.config_file_abs_path)
            exit(1)

        self.config_prefix = config_prefix

        parser = configparser.RawConfigParser()
        readonly_parser = configparser.RawConfigParser()

        if self.config_file_abs_path is not None:
            parser.read([self.config_file_abs_path])
            readonly_parser.read([self.config_file_abs_path])

        self.parser = parser
        self.readonly_parser = readonly_parser

    @property
    def init_dict(self):
        return dict(config_file=self.config_file, config_prefix=self.config_prefix)

    @property
    def api_host(self):
        return self.general_config.get('api_host', default_api_host)

    @property
    def host(self):
        host = self.general_config.get('host', default_host)

        if not host.startswith('http://') and not host.startswith('https://'):
            host = 'https://' + host

        return host

    @property
    def client_id(self):
        return self.general_config.get('client_id', default_client_id)

    @property
    def auth0(self):
        return self.general_config.get('auth0', default_auth0)

    def get_prefix_section(self, section):
        from mali_commands.commons import get_prefix_section

        return get_prefix_section(self.config_prefix, section)

    @property
    def token_config(self):
        section_name = self.get_prefix_section('token')
        return self.items(section_name)

    @property
    def general_config(self):
        return self.readonly_items('general', most_exists=self.config_prefix is not None)

    @property
    def refresh_token(self):
        return self.token_config.get('refresh_token')

    @property
    def id_token(self):
        return self.token_config.get('id_token')

    @property
    def user_id(self):
        import jwt

        data = jwt.decode(self.id_token, verify=False) if self.id_token else {}

        return data.get('user_external_id')

    @classmethod
    def items_from_parse(cls, parser, section, most_exists):
        try:
            return dict(parser.items(section))
        except configparser.NoSectionError:
            if most_exists:
                raise

            return {}

    def items(self, section, most_exists=False):
        return self.items_from_parse(self.parser, section, most_exists=most_exists)

    def readonly_items(self, section, most_exists=False):
        return self.items_from_parse(self.readonly_parser, section, most_exists=most_exists)

    def set(self, section, key, val):
        try:
            self.parser.add_section(section)
        except configparser.DuplicateSectionError:
            pass

        self.parser.set(section, key, val)

    def _write(self, fo):
        self.parser.write(fo)

    def save(self):
        # we always save the config prefix file into the default folder
        if self.config_file_abs_path is None:
            self.config_file_abs_path = find_first_file(self.config_prefix, _missing_link_config) if not self.config_prefix else None
            self.config_file_abs_path = self.config_file_abs_path or default_config_file(self.config_prefix, _missing_link_config)

        create_dir(os.path.dirname(self.config_file_abs_path))

        with open(self.config_file_abs_path, 'w') as configfile:
            self._write(configfile)

    def update_and_save(self, d):
        for section, section_values in d.items():
            section_name_with_prefix = self.get_prefix_section(section)
            for key, val in section_values.items():
                self.set(section_name_with_prefix, key, val)

        self.save()
