from __future__ import unicode_literals

from collections import Sequence
import os
from collections import namedtuple

from mkdocs import utils, theme, plugins
from mkdocs.config.base import Config, ValidationError


class BaseConfigOption(object):

    def __init__(self):
        self.warnings = []
        self.default = None

    def is_required(self):
        return False

    def validate(self, value):
        return self.run_validation(value)

    def reset_warnings(self):
        self.warnings = []

    def pre_validation(self, config, key_name):
        """
        Before all options are validated, perform a pre-validation process.

        The pre-validation process method should be implemented by subclasses.
        """

    def run_validation(self, value):
        """
        Perform validation for a value.

        The run_validation method should be implemented by subclasses.
        """
        return value

    def post_validation(self, config, key_name):
        """
        After all options have passed validation, perform a post-validation
        process to do any additional changes dependant on other config values.

        The post-validation process method should be implemented by subclasses.
        """


class SubConfig(BaseConfigOption, Config):
    def __init__(self, *config_options):
        BaseConfigOption.__init__(self)
        Config.__init__(self, config_options)
        self.default = {}

    def validate(self, value):
        self.load_dict(value)
        return self.run_validation(value)

    def run_validation(self, value):
        Config.validate(self)
        return self


class ConfigItems(BaseConfigOption):
    """
    Config Items Option

    Validates a list of mappings that all must match the same set of
    options.
    """
    def __init__(self, *config_options, **kwargs):
        BaseConfigOption.__init__(self)
        self.item_config = SubConfig(*config_options)
        self.required = kwargs.get('required', False)

    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__, self.item_config)

    def run_validation(self, value):
        if value is None:
            if self.required:
                raise ValidationError("Required configuration not provided.")
            else:
                return ()

        if not isinstance(value, Sequence):
            raise ValidationError('Expected a sequence of mappings, but a %s '
                                  'was given.' % type(value))
        result = []
        for item in value:
            result.append(self.item_config.validate(item))
        return result


class OptionallyRequired(BaseConfigOption):
    """
    A subclass of BaseConfigOption that adds support for default values and
    required values. It is a base class for config options.
    """

    def __init__(self, default=None, required=False):
        super(OptionallyRequired, self).__init__()
        self.default = default
        self.required = required

    def is_required(self):
        return self.required

    def validate(self, value):
        """
        Perform some initial validation.

        If the option is empty (None) and isn't required, leave it as such. If
        it is empty but has a default, use that. Finally, call the
        run_validation method on the subclass unless.
        """

        if value is None:
            if self.default is not None:
                if hasattr(self.default, 'copy'):
                    # ensure no mutable values are assigned
                    value = self.default.copy()
                else:
                    value = self.default
            elif not self.required:
                return
            elif self.required:
                raise ValidationError("Required configuration not provided.")

        return self.run_validation(value)


class Type(OptionallyRequired):
    """
    Type Config Option

    Validate the type of a config option against a given Python type.
    """

    def __init__(self, type_, length=None, **kwargs):
        super(Type, self).__init__(**kwargs)
        self._type = type_
        self.length = length

    def run_validation(self, value):

        if not isinstance(value, self._type):
            msg = ("Expected type: {0} but received: {1}"
                   .format(self._type, type(value)))
        elif self.length is not None and len(value) != self.length:
            msg = ("Expected type: {0} with length {2} but received: {1} with "
                   "length {3}").format(self._type, value, self.length,
                                        len(value))
        else:
            return value

        raise ValidationError(msg)


class Deprecated(BaseConfigOption):

    def __init__(self, moved_to=None):
        super(Deprecated, self).__init__()
        self.default = None
        self.moved_to = moved_to

    def pre_validation(self, config, key_name):

        if config.get(key_name) is None or self.moved_to is None:
            return

        warning = ('The configuration option {0} has been deprecated and will '
                   'be removed in a future release of MkDocs.')
        self.warnings.append(warning)

        if '.' not in self.moved_to:
            target = config
            target_key = self.moved_to
        else:
            move_to, target_key = self.moved_to.rsplit('.', 1)

            target = config
            for key in move_to.split('.'):
                target = target.setdefault(key, {})

                if not isinstance(target, dict):
                    # We can't move it for the user
                    return

        target[target_key] = config.pop(key_name)


class IpAddress(OptionallyRequired):
    """
    IpAddress Config Option

    Validate that an IP address is in an apprioriate format
    """

    def run_validation(self, value):
        try:
            host, port = value.rsplit(':', 1)
        except:
            raise ValidationError("Must be a string of format 'IP:PORT'")

        try:
            port = int(port)
        except:
            raise ValidationError("'{0}' is not a valid port".format(port))

        class Address(namedtuple('Address', 'host port')):
            def __str__(self):
                return '{0}:{1}'.format(self.host, self.port)

        return Address(host, port)


class URL(OptionallyRequired):
    """
    URL Config Option

    Validate a URL by requiring a scheme is present.
    """

    def __init__(self, default='', required=False):
        super(URL, self).__init__(default, required)

    def run_validation(self, value):
        if value == '':
            return value

        try:
            parsed_url = utils.urlparse(value)
        except (AttributeError, TypeError):
            raise ValidationError("Unable to parse the URL.")

        if parsed_url.scheme:
            return value

        raise ValidationError(
            "The URL isn't valid, it should include the http:// (scheme)")


class RepoURL(URL):
    """
    Repo URL Config Option

    A small extension to the URL config that sets the repo_name and edit_uri,
    based on the url if they haven't already been provided.
    """

    def post_validation(self, config, key_name):
        repo_host = utils.urlparse(config['repo_url']).netloc.lower()
        edit_uri = config.get('edit_uri')

        # derive repo_name from repo_url if unset
        if config['repo_url'] is not None and config.get('repo_name') is None:
            if repo_host == 'github.com':
                config['repo_name'] = 'GitHub'
            elif repo_host == 'bitbucket.org':
                config['repo_name'] = 'Bitbucket'
            else:
                config['repo_name'] = repo_host.split('.')[0].title()

        # derive edit_uri from repo_name if unset
        if config['repo_url'] is not None and edit_uri is None:
            if repo_host == 'github.com':
                edit_uri = 'edit/master/docs/'
            elif repo_host == 'bitbucket.org':
                edit_uri = 'src/default/docs/'
            else:
                edit_uri = ''

        # ensure a well-formed edit_uri
        if edit_uri:
            if not edit_uri.startswith(('?', '#')) \
                    and not config['repo_url'].endswith('/'):
                edit_uri = '/' + edit_uri
            if not edit_uri.endswith('/'):
                edit_uri += '/'

        config['edit_uri'] = edit_uri


class FilesystemObject(Type):
    """
    Base class for options that point to filesystem objects.
    """
    def __init__(self, exists=False, **kwargs):
        super(FilesystemObject, self).__init__(type_=utils.string_types, **kwargs)
        self.exists = exists

    def run_validation(self, value):
        value = super(FilesystemObject, self).run_validation(value)
        if self.exists and not self.existence_test(value):
            raise ValidationError("The path {path} isn't an existing {name}.".
                                  format(path=value, name=self.name))
        return os.path.abspath(value)


class Dir(FilesystemObject):
    """
    Dir Config Option

    Validate a path to a directory, optionally verifying that it exists.
    """
    existence_test = staticmethod(os.path.isdir)
    name = 'directory'

    def post_validation(self, config, key_name):

        # Validate that the dir is not the parent dir of the config file.
        if os.path.dirname(config['config_file_path']) == config[key_name]:
            raise ValidationError(
                ("The '{0}' should not be the parent directory of the config "
                 "file. Use a child directory instead so that the config file "
                 "is a sibling of the config file.").format(key_name))


class File(FilesystemObject):
    """
    File Config Option

    Validate a path to a file, optionally verifying that it exists.
    """
    existence_test = staticmethod(os.path.isfile)
    name = 'file'


class SiteDir(Dir):
    """
    SiteDir Config Option

    Validates the site_dir and docs_dir directories do not contain each other.
    """

    def post_validation(self, config, key_name):

        super(SiteDir, self).post_validation(config, key_name)

        # Validate that the docs_dir and site_dir don't contain the
        # other as this will lead to copying back and forth on each
        # and eventually make a deep nested mess.
        if (config['docs_dir'] + os.sep).startswith(config['site_dir'].rstrip(os.sep) + os.sep):
            raise ValidationError(
                ("The 'docs_dir' should not be within the 'site_dir' as this "
                 "can mean the source files are overwritten by the output or "
                 "it will be deleted if --clean is passed to mkdocs build."
                 "(site_dir: '{0}', docs_dir: '{1}')"
                 ).format(config['site_dir'], config['docs_dir']))
        elif (config['site_dir'] + os.sep).startswith(config['docs_dir'].rstrip(os.sep) + os.sep):
            raise ValidationError(
                ("The 'site_dir' should not be within the 'docs_dir' as this "
                 "leads to the build directory being copied into itself and "
                 "duplicate nested files in the 'site_dir'."
                 "(site_dir: '{0}', docs_dir: '{1}')"
                 ).format(config['site_dir'], config['docs_dir']))


class ThemeDir(Dir):
    """
    ThemeDir Config Option. Deprecated
    """

    def pre_validation(self, config, key_name):

        if config.get(key_name) is None:
            return

        warning = ('The configuration option {0} has been deprecated and will '
                   'be removed in a future release of MkDocs.')
        self.warnings.append(warning)

    def post_validation(self, config, key_name):
        # The validation in the parent class this inherits from is not relevant here.
        pass


class Theme(BaseConfigOption):
    """
    Theme Config Option

    Validate that the theme exists and build Theme instance.
    """

    def __init__(self, default=None):
        super(Theme, self).__init__()
        self.default = default

    def validate(self, value):
        if value is None and self.default is not None:
            value = {'name': self.default}

        if isinstance(value, utils.string_types):
            value = {'name': value}

        themes = utils.get_theme_names()

        if isinstance(value, dict):
            if 'name' in value:
                if value['name'] is None or value['name'] in themes:
                    return value

                raise ValidationError(
                    "Unrecognised theme name: '{0}'. The available installed themes "
                    "are: {1}".format(value['name'], ', '.join(themes))
                )

            raise ValidationError("No theme name set.")

        raise ValidationError('Invalid type "{0}". Expected a string or key/value pairs.'.format(type(value)))

    def post_validation(self, config, key_name):
        theme_config = config[key_name]

        # TODO: Remove when theme_dir is fully deprecated.
        if config['theme_dir'] is not None:
            if 'custom_dir' not in theme_config:
                # Only pass in 'theme_dir' if it is set and 'custom_dir' is not set.
                theme_config['custom_dir'] = config['theme_dir']
            if not any(['theme' in c for c in config.user_configs]):
                # If the user did not define a theme, but did define theme_dir, then remove default set in validate.
                theme_config['name'] = None

        if not theme_config['name'] and 'custom_dir' not in theme_config:
            raise ValidationError("At least one of 'theme.name' or 'theme.custom_dir' must be defined.")

        # Ensure custom_dir is an absolute path
        if 'custom_dir' in theme_config and not os.path.isabs(theme_config['custom_dir']):
            theme_config['custom_dir'] = os.path.abspath(theme_config['custom_dir'])

        config[key_name] = theme.Theme(**theme_config)


class Extras(OptionallyRequired):
    """
    Extras Config Option

    Validate the extra configs are a list and issue a warning for any files
    found in the docs_dir which are not listed here.

    TODO: Delete this in a future release and use
    `config_options.Type(list, default=[])` instead.
    """

    def __init__(self, file_match=None, **kwargs):
        super(Extras, self).__init__(**kwargs)
        self.file_match = file_match

    def run_validation(self, value):
        if isinstance(value, list):
            return list(os.path.normcase(path) for path in value)
        else:
            raise ValidationError(
                "Expected a list, got {0}".format(type(value)))

    def walk_docs_dir(self, docs_dir):
        if self.file_match is None:
            raise StopIteration

        for (dirpath, dirs, filenames) in os.walk(docs_dir, followlinks=True):
            dirs.sort()
            for filename in sorted(filenames):
                fullpath = os.path.join(dirpath, filename)

                # Some editors (namely Emacs) will create temporary symlinks
                # for internal magic. We can just ignore these files.
                if os.path.islink(fullpath):
                    local_fullpath = os.path.join(dirpath, os.readlink(fullpath))
                    if not os.path.exists(local_fullpath):
                        continue

                relpath = os.path.normpath(os.path.relpath(fullpath, docs_dir))
                if self.file_match(relpath):
                    yield relpath

    def post_validation(self, config, key_name):
        missing_extras = []
        for filename in self.walk_docs_dir(config['docs_dir']):
            if filename not in config[key_name]:
                missing_extras.append(filename)

        if missing_extras:
            self.warnings.append((
                "Some files in your 'docs_dir' are not listed in the '{0}' "
                "config setting and will be ignored by the theme. Add the "
                "following files to the '{0}' config setting if you want "
                "them to have an effect on the theme: ['{1}']"
            ).format(key_name, "', '".join(missing_extras)))


class Pages(OptionallyRequired):
    """
    Pages Config Option

    Validate the pages config. Automatically add all markdown files if empty.
    """

    def __init__(self, **kwargs):
        super(Pages, self).__init__(**kwargs)
        self.file_match = utils.is_markdown_file

    def run_validation(self, value):

        if not isinstance(value, list):
            raise ValidationError(
                "Expected a list, got {0}".format(type(value)))

        if len(value) == 0:
            return

        config_types = set(type(l) for l in value)
        if config_types.issubset({utils.text_type, dict, str}):
            return value

        raise ValidationError("Invalid pages config. {0} {1}".format(
            config_types, {utils.text_type, dict}
        ))

    def walk_docs_dir(self, docs_dir):

        if self.file_match is None:
            raise StopIteration

        for (dirpath, dirs, filenames) in os.walk(docs_dir, followlinks=True):
            dirs.sort()
            for filename in sorted(filenames):
                fullpath = os.path.join(dirpath, filename)

                # Some editors (namely Emacs) will create temporary symlinks
                # for internal magic. We can just ignore these files.
                if os.path.islink(fullpath):
                    local_fullpath = os.path.join(dirpath, os.readlink(fullpath))
                    if not os.path.exists(local_fullpath):
                        continue

                relpath = os.path.normpath(os.path.relpath(fullpath, docs_dir))
                if self.file_match(relpath):
                    yield relpath

    def post_validation(self, config, key_name):

        if config[key_name] is not None:
            return

        pages = []

        for filename in self.walk_docs_dir(config['docs_dir']):

            if os.path.splitext(filename)[0] == 'index':
                pages.insert(0, filename)
            else:
                pages.append(filename)

        config[key_name] = utils.nest_paths(pages)


class Private(OptionallyRequired):
    """
    Private Config Option

    A config option only for internal use. Raises an error if set by the user.
    """

    def run_validation(self, value):
        raise ValidationError('For internal use only.')


class MarkdownExtensions(OptionallyRequired):
    """
    Markdown Extensions Config Option

    A list of extensions. If a list item contains extension configs,
    those are set on the private  setting passed to `configkey`. The
    `builtins` keyword accepts a list of extensions which cannot be
    overriden by the user. However, builtins can be duplicated to define
    config options for them if desired.
    """
    def __init__(self, builtins=None, configkey='mdx_configs', **kwargs):
        super(MarkdownExtensions, self).__init__(**kwargs)
        self.builtins = builtins or []
        self.configkey = configkey
        self.configdata = {}

    def run_validation(self, value):
        if not isinstance(value, (list, tuple)):
            raise ValidationError('Invalid Markdown Extensions configuration')
        extensions = []
        for item in value:
            if isinstance(item, dict):
                if len(item) > 1:
                    raise ValidationError('Invalid Markdown Extensions configuration')
                ext, cfg = item.popitem()
                extensions.append(ext)
                if cfg is None:
                    continue
                if not isinstance(cfg, dict):
                    raise ValidationError('Invalid config options for Markdown '
                                          "Extension '{0}'.".format(ext))
                self.configdata[ext] = cfg
            elif isinstance(item, utils.string_types):
                extensions.append(item)
            else:
                raise ValidationError('Invalid Markdown Extensions configuration')
        return utils.reduce_list(self.builtins + extensions)

    def post_validation(self, config, key_name):
        config[self.configkey] = self.configdata


class Plugins(OptionallyRequired):
    """
    Plugins config option.

    A list of plugins. If a plugin defines config options those are used when
    initializing the plugin class.
    """

    def __init__(self, **kwargs):
        super(Plugins, self).__init__(**kwargs)
        self.installed_plugins = plugins.get_plugins()

    def run_validation(self, value):
        if not isinstance(value, (list, tuple)):
            raise ValidationError('Invalid Plugins configuration. Expected a list of plugins')
        plgins = plugins.PluginCollection()
        for item in value:
            if isinstance(item, dict):
                if len(item) > 1:
                    raise ValidationError('Invalid Plugins configuration')
                name, cfg = item.popitem()
                cfg = cfg or {}  # Users may define a null (None) config
                if not isinstance(cfg, dict):
                    raise ValidationError('Invalid config options for '
                                          'the "{0}" plugin.'.format(name))
                plgins[name] = self.load_plugin(name, cfg)
            elif isinstance(item, utils.string_types):
                plgins[item] = self.load_plugin(item, {})
            else:
                raise ValidationError('Invalid Plugins configuration')
        return plgins

    def load_plugin(self, name, config):
        if name not in self.installed_plugins:
            raise ValidationError('The "{0}" plugin is not installed'.format(name))

        Plugin = self.installed_plugins[name].load()

        if not issubclass(Plugin, plugins.BasePlugin):
            raise ValidationError('{0}.{1} must be a subclass of {2}.{3}'.format(
                Plugin.__module__, Plugin.__name__, plugins.BasePlugin.__module__,
                plugins.BasePlugin.__name__))

        plugin = Plugin()
        errors, warnings = plugin.load_config(config)
        self.warnings.extend(warnings)
        errors_message = '\n'.join(
            "Plugin value: '{}'. Error: {}".format(x, y)
            for x, y in errors
        )
        if errors_message:
            raise ValidationError(errors_message)
        return plugin
