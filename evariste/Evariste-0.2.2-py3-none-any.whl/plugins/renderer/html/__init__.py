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

"""Render tree as an HTML (body) page."""

import datetime
import logging

from evariste import VERSION
from evariste.plugins.renderer.html import target, readme
from evariste.plugins.renderer.jinja2 import JinjaRenderer
from evariste.utils import expand_path, smart_open

class HTMLRenderer(JinjaRenderer):
    """Render tree as an HTML div (without the `<div>` tags)."""
    # pylint: disable=too-few-public-methods

    keyword = "renderer.html"
    extension = "html"
    description = "Render as an html div"
    default_setup = {
        "href_prefix": "",
        "destfile": 'index.html',
        }
    depends = {
        'suggested': [
            'renderer.html.readme.html',
            'renderer.html.target.default',
        ],
    }
    default_templatevar = {
        "aftertree": 'Generated using <a href="http://framagit.org/spalax/evariste">Évariste</a> version {}, on {}.'.format( # pylint: disable=line-too-long
            VERSION,
            datetime.datetime.now().strftime("%c"),
            ),
    }

    def render(self, tree):
        rendered = super().render(tree)
        with smart_open(expand_path(self.local.setup['destfile']), 'w') as destfile:
            destfile.write(rendered)
        return rendered
