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

"""Abstract utilities for target renderers using Jinja2."""

from evariste.plugins.renderer import TargetRenderer

class Jinja2TargetRenderer(TargetRenderer):
    """Renderer of target (compiled) files using jinja2"""

    keyword = None
    extension = None
    priority = -float("inf")

    def match(self, dummy):
        """This is the default renderer, that matches everything."""
        return True

    def render(self, tree, context):
        """Render ``tree``, which is a :class:`tree.File`."""
        # pylint: disable=arguments-differ
        return context['render'](
            context,
            tree,
            ["tree_file.{}".format(self.extension)],
            )
