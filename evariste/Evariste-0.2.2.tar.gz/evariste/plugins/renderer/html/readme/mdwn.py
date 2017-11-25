# Copyright Louis Paternault 2017
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""IkiWiki markdown README renderer"""

import markdown

from evariste.plugins.renderer.html.readme import HtmlRenderer

class MdwnRenderer(HtmlRenderer):
    """Markdown renderer for readme files."""

    keyword = "renderer.html.readme.mdwn"
    extensions = ["mdwn", "md"]

    def render(self, path, context):
        """Render file as html code.
        """
        with open(path, encoding="utf8") as source:
            return markdown.markdown(source.read())
