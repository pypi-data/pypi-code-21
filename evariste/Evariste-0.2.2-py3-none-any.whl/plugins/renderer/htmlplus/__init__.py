# Copyright Louis Paternault 2017
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

"""Render tree as an HTML (body) page, with CSS"""

import datetime
import os
import pkg_resources

from evariste import VERSION
from evariste import utils
from evariste.plugins.renderer.html import HTMLRenderer

class HTMLPlusRenderer(HTMLRenderer):
    """Render tree as an HTML div (without the `<div>` tags)."""
    # pylint: disable=too-few-public-methods

    keyword = "renderer.htmlplus"
    default_setup = {
        "template": "page.html",
        "display_log": "errors",
        }
    depends = {
        'required': [
            'copy',
        ],
        'suggested': [
            'renderer.html.readme.html',
            'renderer.html.target.image',
            'renderer.html.target.default',
        ],
    }
    default_templatevar = {
        "aftertree": """
            Generated using <a href="http://framagit.org/spalax/evariste">Évariste</a> version {}, on {}.
            Icons from the <a href="https://techbase.kde.org/Projects/Oxygen">KDE Oxygen</a> project.
            """.format(
                VERSION,
                datetime.datetime.now().strftime("%c"),
                ),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.environment.filters['labelize'] = self._labelize
        if 'copy_htmlplus' not in self.shared.setup['copy']:
            self.shared.setup['copy']['copy_htmlplus'] = (
                pkg_resources.resource_filename(
                    self.__class__.__module__,
                    os.path.join("data", "static"),
                    ),
                utils.expand_path(self.local.setup['staticdir']),
                )

    @staticmethod
    def _labelize(string):
        """Return a label, given a string.

        The label starts with alphabetical ascii characters, followed by
        digits. Two different strings have different hashes.
        """
        return "label" + str(hash(string))

    def _templatedirs(self):
        yield from super()._templatedirs()
        yield pkg_resources.resource_filename(
            "evariste.plugins.renderer.html",
            os.path.join("data", "templates"),
            )
