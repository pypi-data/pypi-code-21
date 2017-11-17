"""
"""
from abc import ABC, abstractmethod
from collections import OrderedDict
import enum
import importlib
from pkg_resources import iter_entry_points
import sys

# ProgressMeter statuses
class Status(enum.Enum):
    UNSTARTED = 0
    STARTED = 1
    FINISHED = 2


class ProgressMeterError(Exception):
    pass


class PluginManager:
    def __init__(self):
        self.plugins = None

    def set_plugin_options(self, config=None, **kwargs):
        pass

    def load_plugins(self, names=None, exclusive=False):
        plugins = {}
        for entry_point in iter_entry_points(group='pokrok'):
            plugin = entry_point.load()
            if plugin.installed:
                plugins[entry_point.name] = plugin

        if names:
            ordered_plugins = OrderedDict()
            for name in names:
                if name in plugins:
                    ordered_plugins[name] = plugins[name]
            if not exclusive:
                for name in (set(plugins.keys()) - set(ordered_plugins.keys())):
                    ordered_plugins[name] = plugins[name]
            self.plugins = ordered_plugins
        else:
            self.plugins = plugins

    def has_plugin(self, name):
        if not self.plugins:
            self.load_plugins()
        return name in self.plugins

    def get_plugin(self, name):
        if not self.has_plugin(name):
            raise ValueError("No such plugin: {}".format(name))
        if isinstance(self.plugins[name], type):
            self.plugins[name] = self.plugins[name]()
        return self.plugins[name]

    def get_first_plugin(self, sized=None, widgets=None):
        """Returns the first plugin that can provide a progress meter of the
        specified configuration.

        Args:
            sized: Whether a sized ProgressMeter is required.
            widgets: The desired style.

        Returns:
            A ProgressMeter instance if one is found that can provide the
            specified configuration, else None.
        """
        if self.plugins is None:
            self.load_plugins()

        if len(self.plugins) == 0:
            return None

        plugin_names = tuple(self.plugins.keys())
        if sized is None and widgets is None:
            return self.get_plugin(plugin_names[0])

        for plugin_name in plugin_names:
            plugin = self.get_plugin(plugin_name)
            if plugin.provides(sized, widgets):
                return plugin

        return None


class ProgressMeterFactory(ABC):
    """Plugin base class. A plugin's entry point must provide an instance of
    a ProgressMeterFactory.
    """
    @property
    @abstractmethod
    def name(self):
        """The plugin's name.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def installed(self):
        """Import the package(s) depended upon by this module.

        Returns:
            True if all required packages are successfully imported.
        """
        raise NotImplementedError()

    @abstractmethod
    def provides(self, sized, widgets=None):
        """Whether the plugin can provide a progress meter that conforms to the
        specified style. The plugin is free to interpret this request as it sees
        fit, including ignoring or substituting widgets.

        Args:
            sized: Boolean, whether the user is requesting a sized progress
                meter.
            widgets: The Style requested, or None to use the plugin's default
                style.

        Returns:
            True if the plugin can provide a conforming progress meter.
        """
        raise NotImplementedError()

    @abstractmethod
    def create(self, size=None, widgets=None, desc=None, start=None, **kwargs):
        """Create a progress meter that conforms to the requested style.

        Args:
            size: Size of the progress meter.
            widgets: The desired style, or None to use the plugin's default
                style.
            desc: String description to print next to the progress bar.
            start: Counter start value.
            kwargs: Additional keyword arguments to pass to the underlying
                progress meter package. The plugin is free to interpret these
                arguments as it wishes, including ignoring them.

        Returns:
            A ProgressMeter instance.
        """
        raise NotImplementedError()

    @abstractmethod
    def iterate(
            self, iterable, size=None, widgets=None, desc=None, start=None,
            **kwargs):
        """Wrap an iterable with a progress meter.

        Args:
            iterable: The iterable to wrap.
            size: Size of the progress meter.
            widgets: The desired style, or None to use the plugin's default
                style.
            desc: String description to print next to the progress bar.
            start: Counter start value.
            kwargs: Additional keyword arguments to pass to the underlying
                progress meter package. The plugin is free to interpret these
                arguments as it wishes, including ignoring them.

        Returns:
            An iterable. Returns the original iterable if there were any
            problems creating the wrapper.

        """
        raise NotImplementedError()


class DefaultProgressMeterFactory(ProgressMeterFactory):
    """Default implementation of ProgressMeterFactory. Assumes that a) the
    underlying package is in a module that can be imported using importlib
    (if it is installed), b) the package supports any desired progress
    meter configuration (override `provides` if this isn't true), and c)
    the ProgressMeter subclass has a constructor with signature
    (module, size, widgets, desc, start, **kwargs).

    Args:
        name: The plugin name. Also used as the module name if `module_name`
            is None.
        progress_meter_class: The ProgressMeter subclass to instantiate.
        style_superset: A Style object that lists all of the widgets supported
            by the plugin.
        module_name: The name of the module, if different from `name`.
    """
    def __init__(
            self, name, progress_meter_class, style_superset,
            module_name=None):
        super().__init__()
        self._name = name
        self._package = module_name or name
        self._module = None
        self._progress_meter_class = progress_meter_class
        self._style_superset = style_superset

    @property
    def name(self):
        return self._name

    def installed(self):
        return self._load_module()


    def provides(self, sized, widgets=None):
        if not (widgets and self._style_superset):
            return True

        provided_widgets = self._style_superset.get_widgets(sized)
        if not provided_widgets:
            return False

        return len(set(widgets) - set(provided_widgets)) == 0

    def create(self, size=None, widgets=None, desc=None, start=None, **kwargs):
        self._load_module()
        return self._progress_meter_class(
            module=self._module, size=None, widgets=None, desc=None, start=None,
            **kwargs)

    def iterate(
            self, iterable, size=None, widgets=None, desc=None, start=None,
            **kwargs):
        pbar = self.create(size, widgets, desc, start, **kwargs)
        if pbar:
            with pbar:
                for item in iterable:
                    yield item
                    pbar.increment()
        else:
            return iterable

    def _load_module(self):
        if self._module is None:
            try:
                self._module = importlib.import_module(self._package)
            except ImportError:
                self._module = False
        return self._module not in (None, False)


class ProgressMeter(ABC):
    """ProgressMeter interface to be implemented by the plugin.
    """
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

    @property
    @abstractmethod
    def is_sized(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def status(self):
        """The current status of the ProgressMeter. Must be one of the
        enumerated values.
        """
        raise NotImplementedError()

    def start(self):
        """Initialize and show the progress meter.
        """
        pass

    def finish(self):
        """Signal that the task is complete. The progress meter should update
        its display accordingly (if applicable).
        """
        pass

    @abstractmethod
    def increment(self, n=1):
        """Increment the progress meter by a fixed amount (default=1).

        Args:
            n: The amount to increment.

        Returns:
            The current value after incrementing.
        """
        raise NotImplementedError()

    def _check_status(self, status=Status.STARTED, error=True):
        """Checks that the ProgressMeter's status matches `stats`.

        Args:
            status: The status to check.
            error: If True, an error is raised if the ProgressMeter does not
                have the specified status.

        Returns:
            True if the ProgressMeter is has the specified status. False if the
            ProgressMeter does not have the specified status and `error` is
            False.

        Raises:
            ProgressMeterError if the ProgressMeter does not have the
            specified status and `error` is True.
        """
        if self.status != status:
            if error:
                raise ProgressMeterError(
                    "The ProgressMeter status {} differs from expected status "
                    "{}".format(self.status, status))
            else:
                return False

        return True


class BaseProgressMeter(ProgressMeter):
    """Default implementation of ProgressMeter. Subclasses only need to
    implement `increment()`.
    """
    def __init__(self, size=None):
        self._status = Status.UNSTARTED
        self.size = size

    @property
    def is_sized(self):
        return self.size is not None

    @property
    def status(self):
        return self._status

    def start(self):
        self._check_status(Status.UNSTARTED)
        self._status = Status.STARTED

    def finish(self):
        self._check_status(Status.STARTED)
        self._status = Status.FINISHED


class SimpleTextProgressMeter(BaseProgressMeter):
    """Simplest progress meter implementation. Simply prints a character each
    time it is incremented.
    """
    def __init__(self, char='*', file=sys.stderr, **kwargs):
        super().__init__()
        self.char = char
        self.file = file

    def increment(self, n=1):
        print(self.char * n, file=self.file)
