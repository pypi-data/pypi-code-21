# Copyright Louis Paternault 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Plugin loader"""

import collections
import contextlib
import functools
import logging
import os
import shlex
import sys

from evariste import errors, utils, setup
from evariste.hooks import set_methodhook
import evariste

LOGGER = logging.getLogger(evariste.__name__)

class NoMatch(errors.EvaristeError):
    """No plugin found matching ``value``."""

    def __init__(self, value, available):
        super().__init__()
        self.value = value
        self.available = available

    def __str__(self):
        return "Value '{}' does not match any of {}.".format(
            self.value,
            str(self.available),
            )

class SameKeyword(errors.EvaristeError):
    """Two plugins have the same keyword."""

    def __init__(self, keyword, plugin1, plugin2):
        super().__init__()
        self.keyword = keyword
        self.plugins = (plugin1, plugin2)

    def __str__(self):
        return """Plugins '{}' and '{}' have the same keyword '{}'.""".format(
            self.plugins[0].__name__,
            self.plugins[1].__name__,
            self.keyword,
            )

class NotAPlugin(errors.EvaristeError):
    """Superclass of plugins is not a plugin."""

    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def __str__(self):
        return (
            """Class '{obj.__module__}.{obj.__name__}' is not a plugin """
            """(it should inherit from """
            """'{superclass.__module__}.{superclass.__name__}')."""
            ).format(
                obj=self.obj,
                superclass=PluginBase,
            )

class PluginNotFound(errors.EvaristeError):
    """Plugin cannot be found."""

    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword

    def __str__(self):
        return "Cannot find plugin '{}'.".format(
            self.keyword,
            )

@functools.total_ordering
class PluginBase:
    """Plugin base: all imported plugins must be subclasses of this class."""
    # pylint: disable=too-few-public-methods

    keyword = None
    description = None
    priority = 0
    default_setup = {}
    global_default_setup = {}
    plugin_type = None
    subplugins = {}
    hooks = {}
    depends = {}
    default = False
    required = False

    def __init__(self, shared):
        self.hook_instances = {}
        self.shared = shared
        self.local = shared.get_plugin_view(self.keyword)
        self._set_default_setup()
        self._load_hooks()

    def _set_default_setup(self):
        """Set default value for this plugin setup, if necessary."""
        default = setup.Setup()
        for parent in reversed(self.__class__.mro()): # pylint: disable=no-member
            if hasattr(parent, "default_setup"):
                default.update(parent.global_default_setup)
                default.update({self.keyword: parent.default_setup})
        self.shared.setup.fill_blanks(default)

    def _load_hooks(self):
        """Load hooks."""
        for hook in self.hooks:
            self.hook_instances[hook] = functools.partial(self.hooks[hook], self)

    def match(self, value, *args, **kwargs): # pylint: disable=unused-argument
        """Return ``True`` iff ``value`` matches ``self``.

        Default is keyword match. This method can be overloaded by
        subclasses.
        """
        return value == self.keyword

    def __lt__(self, other):
        priority = self.priority
        if callable(priority):
            priority = priority() # pylint: disable=not-callable
        other_priority = other.priority
        if callable(other_priority):
            other_priority = other_priority()
        if priority == other_priority:
            return self.keyword < other.keyword
        return priority < other_priority

class PluginLoader:
    """Plugin loader. Find plugins and select the appropriate one."""

    def __init__(self, shared, libdirs=None):
        self.plugins = self._load_plugins(
            self._sort_plugins(
                self._list_available_plugins(libdirs)
                ),
            shared,
            )

    @staticmethod
    def _sort_plugins(pluginset):
        """Sort plugins by type and keyword."""
        plugindict = utils.DeepDict(2)

        for plugin in pluginset:
            if plugin.keyword in plugindict[plugin.plugin_type]:
                raise SameKeyword(
                    plugin.keyword,
                    plugin,
                    plugindict[plugin.plugin_type][plugin.keyword],
                    )

            plugindict[plugin.plugin_type][plugin.keyword] = plugin
        return plugindict

    @staticmethod
    def _load_plugins(available, shared):
        """Given the avaialble plugins, only loads relevant plugins.

        :return: A dictionary of loaded (instanciated) plugins.
        """
        # pylint: disable=too-many-branches, too-many-nested-blocks

        # Step 0: Converting setup options in a list of keyword
        for key in ["enable_plugins", "disable_plugins"]:
            if shared.setup['setup'][key] is None:
                shared.setup['setup'][key] = []
            else:
                if isinstance(shared.setup['setup'][key], str):
                    shared.setup['setup'][key] = shlex.split(shared.setup['setup'][key])
                elif isinstance(shared.setup['setup'][key], list):
                    pass
                else:
                    raise ValueError(
                        (
                            "'Setup[setup][enable_plugins]' should be a string or a "
                            "list (is now {}: '{}')."
                        ).format(
                            type(shared.setup['setup'][key]),
                            shared.setup['setup'][key],
                            ))

        # Step 1: Adding default plugins (unless disabled), and required plugins
        plugins = dict()
        for plugin_type in available:
            for keyword in available[plugin_type]:
                if (
                        available[plugin_type][keyword].default
                        and
                        keyword not in shared.setup['setup']['disable_plugins']
                    ):
                    plugins[keyword] = available[plugin_type][keyword]
                if available[plugin_type][keyword].required:
                    if keyword in shared.setup['setup']["disable_plugins"]:
                        LOGGER.warning(
                            (
                                "Disabling plugin '{}' is asked by setup, "
                                "but it is required. Still enabling."
                            ).format(keyword)
                            )
                    plugins[keyword] = available[plugin_type][keyword]

        # Step 2: Adding enabled plugins
        for keyword in shared.setup['setup']["enable_plugins"]:
            try:
                plugins[keyword] = available.get_subkey(keyword)
            except KeyError:
                raise PluginNotFound(keyword)

        # Step 3: Managing dependencies
        to_process = list(plugins.values())
        while to_process:
            plugin = to_process.pop()
            for keyword in plugin.depends.get('required', ()):
                try:
                    required = available.get_subkey(keyword)
                except KeyError:
                    raise PluginNotFound(keyword)
                if keyword not in plugins:
                    if keyword in shared.setup['setup']["disable_plugins"]: # pylint: disable=line-too-long
                        LOGGER.warning(
                            (
                                "Disabling plugin '{}' is asked by "
                                "setup, but it is required. Still "
                                "enabling."
                            ).format(keyword)
                        )
                    plugins[keyword] = required
                    to_process.append(required)
            for keyword in plugin.depends.get('suggested', ()):
                try:
                    suggested = available.get_subkey(keyword)
                except KeyError:
                    LOGGER.warning(
                        (
                            "Ignoring plugin '{}' required by "
                            "'{}': plugin not found."
                        ).format(
                            keyword, plugin.keyword,
                        ))
                    continue
                if suggested.keyword not in plugins:
                    if suggested.keyword in shared.setup['setup']["disable_plugins"]:
                        continue
                    plugins[suggested.keyword] = suggested
                    to_process.append(suggested)

        # Step 4: Instanciating plugins
        loaded = collections.defaultdict(dict)
        for keyword in plugins:
            loaded[plugins[keyword].plugin_type][keyword] = plugins[keyword](shared)

        return loaded

    @staticmethod
    def _list_available_plugins(libdirs):
        """Look for available plugins in accessible packages.

        Return a set of available plugins.
        """
        plugins = set()
        if libdirs is None:
            libdirs = []

        path = []
        path.extend([
            os.path.join(utils.expand_path(item), "plugins")
            for item
            in [".evariste", "~/.config/evariste", "~/.evariste"]
            ])
        path.extend([utils.expand_path(item) for item in libdirs])
        path.extend([
            os.path.join(item, "evariste")
            for item
            in sys.path
            ])

        for module in utils.iter_modules(path, "evariste.", LOGGER.debug):
            for attr in dir(module):
                if attr.startswith("_"):
                    continue
                obj = getattr(module, attr)

                if (
                        isinstance(obj, type)
                        and
                        issubclass(obj, PluginBase)
                    ):
                    if obj.keyword is None:
                        continue
                    plugins.add(obj)
        return plugins

    def match(self, plugin_type, value):
        """Return the first plugin matching ``value``.

        A plugin ``Foo`` matches ``value`` if ``Foo.match(value)`` returns
        True.
        """
        for plugin in sorted(self.get_plugin_type(plugin_type).values(), reverse=True):
            if plugin.match(value):
                return plugin
        raise NoMatch(value, sorted(self.iter_keywords(plugin_type)))

    def iter_pluginkeywords(self, plugin_type=None):
        """Iterate over plugin keywords."""
        for plugin in self.iter_plugins(plugin_type):
            yield plugin.keyword

    def iter_plugins(self, plugin_type=None):
        """Iterate over plugins."""
        if plugin_type is None:
            for ptype in self.plugins:
                for keyword in self.get_plugin_type(ptype):
                    yield self.get_plugin_type(ptype)[keyword]
        else:
            for keyword in self.get_plugin_type(plugin_type):
                yield self.get_plugin_type(plugin_type)[keyword]

    def iter_keywords(self, plugin_type=None):
        """Iterate over keywords"""
        if plugin_type is None:
            for ptype in self.plugins:
                yield from self.get_plugin_type(ptype)
        else:
            yield from self.get_plugin_type(plugin_type)

    def get_plugin_type(self, plugin_type):
        """Return a dictionary of plugins of the given type.

        This dictionary is indexed by plugin keywords.
        """
        return self.plugins[plugin_type]

    def get_plugin(self, keyword):
        """Return the plugin with the given keyword."""
        for plugin in self.iter_plugins():
            if plugin.keyword == keyword:
                return plugin
        raise KeyError(keyword)


def get_plugins(self, *_args, **_kwargs):
    """Given a :class:`AllPlugins` object, return itself.

    Useful to give hooks the plugins object.
    """
    return self

def get_libdirs(libdirs):
    """Convert `libdirs` setup option (as a string) to a list of path (as strings).
    """
    if libdirs:
        return shlex.split(libdirs)
    else:
        return []

class AllPlugins:
    """Gather all used plugins."""
    # pylint: disable=too-few-public-methods

    @set_methodhook("load_plugins", getter=get_plugins)
    def __init__(self, *, shared):
        self.shared = shared
        self.plugins = PluginLoader(
            shared,
            get_libdirs(shared.setup['setup']['libdirs']),
            )

    def iter_plugins(self, *args, **kwargs):
        """Iterate over loaded plugins."""
        yield from self.plugins.iter_plugins(*args, **kwargs)

    def _iter_hooks(self, name):
        """Iterator over functions registered for hook ``name``."""
        for plugin in self.iter_plugins():
            if name in plugin.hook_instances:
                yield plugin.hook_instances[name](self.shared)

    @contextlib.contextmanager
    def apply_context_hook(self, hookname, *, args=None, kwargs=None):
        """Apply a context hook (that is, run stuff before and after a `with` context).

        :param str hookname: Name of the hook to apply.
        :param list args: List of parameters to pass to hooks and
            ``function``.
        :param dict kwargs: Dictionary of parameters to pass to hooks and
            ``function``.
        """
        if args is None:
            args = list()
        if kwargs is None:
            kwargs = dict()
        hooks = None

        if hasattr(self, "plugins"):
            if hooks is None:
                hooks = list(self._iter_hooks(hookname))
            for hook in hooks:
                returnvalue = hook.enter(*args, **kwargs)
                if returnvalue is not None:
                    args, kwargs = returnvalue

        yield

        if hooks is None:
            hooks = list(self._iter_hooks(hookname))
        for hook in hooks:
            hook.exit()

    def apply_method_hook(self, hookname, function, *, args=None, kwargs=None):
        """Apply a method hook (that is, run stuff before and after a method call).

        :param str hookname: Name of the hook to apply.
        :param function function: Function to which the hook is to be applied.
        :param list args: List of parameters to pass to hooks and
            ``function``.
        :param dict kwargs: Dictionary of parameters to pass to hooks and
            ``function``.
        """
        if args is None:
            args = list()
        if kwargs is None:
            kwargs = dict()
        hooks = None

        if hasattr(self, "plugins"):
            if hooks is None:
                hooks = list(self._iter_hooks(hookname))
            for hook in hooks:
                returnvalue = hook.enter(*args, **kwargs)
                if returnvalue is not None:
                    args, kwargs = returnvalue

        returnvalue = function(*args, **kwargs)

        if hooks is None:
            hooks = list(self._iter_hooks(hookname))
        for hook in hooks:
            returnvalue = hook.exit(returnvalue)
        return returnvalue


    def get_plugin(self, keyword):
        """Return the plugin with the given keyword."""
        return self.plugins.get_plugin(keyword)

    def get_plugin_type(self, plugin_type):
        """Return a dictionary of plugins of the given type."""
        return self.plugins.get_plugin_type(plugin_type)

    def match_plugin(self, *args, **kwargs):
        """Return the first plugin matching the arguments.

        Arguments are transmitted to
        :meth:`evariste.plugins.PluginLoader.match`.
        """
        return self.plugins.match(*args, **kwargs)

    def iter_pluginkeywords(self):
        """Iterate over plugin keyword."""
        yield from self.plugins.iter_pluginkeywords()
