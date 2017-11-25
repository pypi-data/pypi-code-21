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

"""Abstract class for jinja2 renderers."""

import datetime
import os
import pathlib
import textwrap

import jinja2
import pkg_resources

from evariste import utils
from evariste.plugins import NoMatch
from evariste.plugins.renderer.dest import DestRenderer
from evariste.plugins.renderer.jinja2.readme import Jinja2ReadmeRenderer
from evariste.plugins.renderer.jinja2.target import Jinja2TargetRenderer

NOW = datetime.datetime.now()

class JinjaRenderer(DestRenderer):
    """Abstract class for jinja2 renderers."""
    # pylint: disable=too-few-public-methods

    extension = None
    subplugins = {
        "target": Jinja2TargetRenderer,
        "readme": Jinja2ReadmeRenderer,
        }
    default_templatevar = {
        "date": NOW.strftime("%x"),
        "time": NOW.strftime("%X"),
        "datetime": NOW.strftime("%c"),
    }

    def __init__(self, shared):
        super().__init__(shared)

        self.environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                self._templatedirs(),
            )
        )
        self.environment.filters['basename'] = os.path.basename
        self.environment.filters['yesno'] = utils.yesno

    def _templatedirs(self):
        """Iterator over the directories in which templates may exist.

        - Directories are returned as strings;
        - directories may not exist.
        """
        if self.local.setup['templatedirs'] is not None:
            yield from utils.expand_path(self.local.setup['templatedirs']).split()
        yield pkg_resources.resource_filename( #pylint: disable=no-member
            self.__class__.__module__,
            os.path.join("data", "templates")
            )
        yield from [
            os.path.join(utils.expand_path(path), "templates")
            for path
            in [".evariste", "~/.config/evariste", "~/.evariste", "/usr/share/evariste"]
            ]

    def _template(self):
        """Return the name of the template to use."""
        if self.local.setup['template'] is not None:
            return self.local.setup['template']
        return "tree.{}".format(self.extension)

    def render(self, tree):
        return self._render(
            tree=tree,
            template=self._template(),
            context={
                'destdir': pathlib.Path(self.destdir),
                'shared': self.shared,
                'local': self.local,
                'render': self._render,
                'sourcepath': self._sourcepath,
                'render_readme': self._render_readme,
                'render_file': self._render_file,
                'render_directory': self._render_directory,
                'render_template': self._render_template,
                'templatevar': self._get_templatevar(),
                },
            )

    def _get_templatevar(self):
        """Return the template variables.

        - First, update it with the default variables of this class
          (`self.default_templatevar`), then its ancestors.
        - Then, update it with the variables defined in the setup file.
        """
        templatevar = {}
        for parent in reversed(self.__class__.mro()): # pylint: disable=no-member
            templatevar.update(getattr(parent, "default_templatevar", {}))
        templatevar.update(self.shared.setup["{}.templatevar".format(self.keyword)])
        return templatevar

    @jinja2.contextfunction
    def _render(self, context, tree, template):
        """Render the tree, using given template (or template list)."""
        if isinstance(context, dict):
            context['tree'] = tree
        else:
            context.vars['tree'] = tree
        if tree.is_file() and tree.report.success:
            utils.copy(
                (tree.root.from_fs / tree.report.target).as_posix(),
                (context['destdir'] / tree.report.target).as_posix(),
                )
        return textwrap.indent(
            self.environment.get_or_select_template(template).render(context),
            "  ",
            )

    @jinja2.contextfunction
    def _render_directory(self, context, tree):
        """Render ``tree``, which is a :class:`tree.Directory`, as HTML."""
        return self._render(context, tree, "tree_directory.{}".format(self.extension))

    @jinja2.contextfunction
    def _render_file(self, context, tree):
        """Render ``tree``, which is a :class:`tree.File`."""
        available = []
        for parent in self.__class__.mro(): # pylint: disable=no-member
            if not hasattr(parent, 'keyword'):
                break
            if parent.keyword is not None:
                available.append(parent.keyword)
            try:
                return self.shared.builder.plugins.match_plugin(
                    "{}.target".format(parent.keyword), tree
                    ).render(tree, context)
            except NoMatch:
                pass
        raise NoMatch(tree, available)

    @jinja2.contextfunction
    def _sourcepath(self, context, tree):
        """Return the path to the source file or archive.

        This functions builds the archive before returning its path. It can be
        called several times: the archive will be built only once.
        """
        # pylint: disable=no-self-use
        return tree.make_archive(context["destdir"])

    @jinja2.contextfunction
    def _render_readme(self, context, tree):
        """Find the readme of tree, and returns the corresponding code."""
        # pylint: disable=unused-argument
        readme = tree.render_readme(self.iter_subplugins("readme"), context)
        if readme:
            return readme
        return ""

    @jinja2.contextfunction
    def _render_template(self, context, template):
        """Render template given in argument."""
        with open(template) as file:
            return self.environment.from_string(file.read()).render(context)
