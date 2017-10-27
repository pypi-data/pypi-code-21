import os
import errno
import logging
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

_logger = logging.getLogger(__name__)


class DeployvConfig(object):

    def __init__(self, config=None):
        self.config = self.parse_config(config)

    def parse_config(self, additional_config_file=None):
        """Loads and returns the parsed config files in a ConfigParser object.

        The config files are loaded in this order:

        1. /etc/deployv/deployv.conf
        2. /etc/deployv/conf.d/*.conf
        3. ~/.config/deployv/deployv.conf
        4. ~/.config/deployv/conf.d/*.conf
        5. All files received in additional_config_files.

        :param additional_config_file: Additional .conf file to load.
        :type additional_config_files: String

        :returns: The parsed config files.
        :rtype: ConfigParser
        """
        config = getattr(self, 'config', None) or ConfigParser()
        default_config_file = 'deployv/config/deployv.conf'
        config_files = [default_config_file]
        main_dirs = ['/etc/deployv', os.path.expanduser('~/.config/deployv')]
        for main_dir in main_dirs:
            main_config_file = os.path.join(main_dir, 'deployv.conf')
            if os.access(main_config_file, os.F_OK):
                config_files.append(main_config_file)
            addons_dir = os.path.join(main_dir, 'conf.d')
            if os.path.isdir(addons_dir):
                for filename in os.listdir(addons_dir):
                    filepath = os.path.join(addons_dir, filename)
                    if os.path.isfile(filepath) and filename.endswith('.conf'):
                        config_files.append(filepath)
        if len(config_files) == 1:
            _logger.warn("Warning: no config file detected in the config "
                         "paths. You can create a `deployv.conf` file in "
                         "`/etc/deployv/` or `~/.config/deployv/` paths. "
                         "You can also run `deployvcmd setup_config` to "
                         "automatically create the config files for you.")
        if additional_config_file:
            config_files.append(additional_config_file)
        if config_files:
            _logger.info("Loading config files: %s", ", ".join(config_files))
            loaded_files = config.read(config_files)
            if len(config_files) != len(loaded_files):
                _logger.warn("Error loading config files: %s",
                             ", ".join(set(config_files) - set(loaded_files)))
        return config

    def setup_config_dirs(self):
        _logger.info("Writing config files")
        default_config_file = 'deployv/config/deployv.conf'
        for main_dir in ['/etc/deployv', os.path.expanduser('~/.config/deployv')]:
            config_file_name = os.path.join(main_dir, 'deployv.conf')
            error_msg = "Couldn't write config file: '%s' (skipped)"
            ok_msg = "Created config file: '%s'"
            addon_dir = os.path.join(main_dir, 'conf.d')
            is_user_dir = os.path.expanduser('~/') in main_dir
            try:
                os.makedirs(addon_dir)
            except OSError as error:
                if error.errno != errno.EEXIST:
                    _logger.warn(error_msg, config_file_name)
                    continue
            else:
                if is_user_dir:
                    for path in [main_dir.replace('/deployv', ''), main_dir, addon_dir]:
                        self._fix_ownership(path)
            config = ConfigParser()
            config.read([default_config_file, config_file_name])
            try:
                with open(config_file_name, 'w+') as config_file:
                    config.write(config_file)
            except (OSError, IOError) as error:
                _logger.warn(error_msg, config_file_name)
            else:
                _logger.info(ok_msg, config_file_name)
                if is_user_dir:
                    self._fix_ownership(config_file_name)
        self.config = self.parse_config()

    def _fix_ownership(self, path):
        uid = os.environ.get('SUDO_UID')
        gid = os.environ.get('SUDO_GID')
        if uid is not None:
            os.chown(path, int(uid), int(gid))


def get_config(config_file=None):
    config = DeployvConfig(config_file)
    return config.config
