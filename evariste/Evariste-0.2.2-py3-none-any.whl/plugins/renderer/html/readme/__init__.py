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

"""Raw README plugin for html renderer."""

from evariste.plugins.renderer.jinja2.readme import Jinja2ReadmeRenderer

class HtmlRenderer(Jinja2ReadmeRenderer):
    """Html renderer for readme files, using jinja2 template engine."""
    # pylint: disable=too-few-public-methods, abstract-method

    plugin_type = "renderer.html.readme"
    keyword = "renderer.html.readme.html"
    extensions = ['html', 'htm']
