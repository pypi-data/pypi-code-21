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

"""Rest README renderer"""

from docutils import core

from evariste.plugins.renderer.html.readme import HtmlRenderer

class RestRenderer(HtmlRenderer):
    """reStructuredText renderer for readme files."""
    # pylint: disable=too-few-public-methods, abstract-method

    keyword = "renderer.html.readme.rst"
    extensions = ["rst", "rest"]

    def render(self, path, context):
        """Render file as html code.
        """
        with open(path) as source:
            return core.publish_parts(
                source=source.read(),
                source_path=path,
                #destination_path=destination_path,
                writer_name='html',
                settings_overrides={
                    #'input_encoding': input_encoding,
                    'doctitle_xform': False,
                    'initial_header_level': 1,
                    }
                )['body']
