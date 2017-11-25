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

"""Provide hook mechanism to builder"""

import functools

class Hook:
    """Hook, containing functions associated to a certain event.
    """
    # pylint: disable=too-few-public-methods

    data = None

    def __init__(self, plugin, shared):
        self.shared = shared
        self.plugin = plugin
        self.local = self.plugin.local

class ContextHook(Hook):
    """Hook executed before and after a context"""

    def enter(self, *args, **kwargs):
        # pylint: disable=no-self-use, unused-argument
        """Hook called before the context.

        Takes as arguments the arguments ``args`` and ``kwargs`` passed to the
        the :meth:`evariste.plugins.AllPlugins.apply_hook` method.

        :return: Nothing.
        """
        return

    def exit(self, value=None):
        # pylint: disable=no-self-use
        """Hook called after the context."""
        return value

def set_methodhook(hookname=None, *, getter=None):
    """Decorator to add hooks to a class method.

    :param str hookname: Name of the hook to register.
    :param function getter: Function that, given the instance object as argument,
        returns a :class:`plugins.AllPlugins` object. If ``None``, the default
        ``self.shared.builder.plugins`` is used (``self`` is supposed to have
        this attribute).
    """

    def decorator(function):
        """Actual decorator."""
        if hookname is None:
            name = function.__name__
        else:
            name = hookname

        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            """Wrapped function."""
            self = args[0]
            if getter is None:
                plugins = self.shared.builder.plugins
            else:
                plugins = getter(*args, **kwargs)

            return plugins.apply_method_hook(name, function, args=args, kwargs=kwargs)

        return wrapped

    return decorator
