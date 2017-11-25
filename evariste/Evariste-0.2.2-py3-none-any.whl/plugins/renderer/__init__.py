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

"""Render (processed) tree: abstract class."""

import glob
import os
import pathlib
import tempfile
import textwrap

from evariste import errors, plugins
from evariste.plugins import NoMatch

################################################################################
# Targets: how should target files be rendererd?
class TargetRenderer(plugins.PluginBase):
    """Renderer of target (compiled) files."""

    def match(self, dummy):
        """This is the default renderer, that matches everything."""
        return True

    def render(self, tree):
        """Render ``tree``, which is a :class:`tree.File`."""
        raise NotImplementedError()

################################################################################
# Readme plugins: annotation of files

class CannotRender(errors.EvaristeError):
    """Exception raised when renderer cannot render a given file."""
    pass

class ReadmeRenderer(plugins.PluginBase):
    """Generic class of README renderers, and also a default raw renderer."""
    # pylint: disable=too-few-public-methods, abstract-method

    extensions = []

    def render(self, path, *args, **kwargs):
        """Render the readme file ``path``.
        """
        # pylint: disable=unused-argument, no-self-use
        with open(path) as file:
            return file.read()

    def iter_readme(self, value, directory):
        """Iterave over potential readme files for the path ``value``."""
        if directory:
            yield from self.iter_readme_dir(value)
        else:
            yield from self.iter_readme_file(value)

    def iter_readme_dir(self, value):
        """Iterate over potential readme for the given directory ``value``."""
        for ext in self.extensions:
            for filename in glob.iglob((value / "*.{}".format(ext)).as_posix()):
                basename = os.path.basename(filename)
                if basename.count(".") == 1:
                    if basename.split(".")[0].lower() == "readme":
                        yield filename

    def iter_readme_file(self, value):
        """Iterate over potential readme for the given file ``value``."""
        for ext in self.extensions:
            for filename in glob.iglob("{}.{}".format(value, ext)):
                yield filename

################################################################################
# Renderer: renders the directory tree into something (html, etc.)

class Renderer(plugins.PluginBase):
    """Abstract tree renderer."""

    plugin_type = "renderer"

    subplugins = {
        "readme": ReadmeRenderer,
        "target": TargetRenderer,
        }

    global_default_setup = {'renderer': {'enable_plugins': ''}}

    def priority(self):
        """Return keyword as priority.

        That way, plugins are sorted by name.
        """
        return self.keyword

    def render(self, tree):
        """Render tree."""
        raise NotImplementedError()

    def iter_subplugins(self, subtype):
        """Iterate over subplugins of type `subtype`."""
        for parent in self.__class__.mro(): # pylint: disable=no-member
            if not hasattr(parent, 'keyword'):
                break
            try:
                yield from self.shared.builder.plugins.get_plugin_type(
                    "{}.{}".format(parent.keyword, subtype)
                    ).values()
            except NoMatch:
                pass

    def prune_readmes(self, tree):
        """Remove readme files from tree."""
        for filename in list(tree.iter_readmes(self.iter_subplugins('readme'))):
            if tree.find(filename):
                tree.prune(filename)
