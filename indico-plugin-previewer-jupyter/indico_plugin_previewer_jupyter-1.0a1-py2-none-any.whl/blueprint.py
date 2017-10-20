# This file is part of Indico.
# Copyright (C) 2002 - 2017 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from indico.core.plugins import IndicoPluginBlueprint

from indico_previewer_jupyter.controllers import RHEventPreviewIPyNB


blueprint = IndicoPluginBlueprint('previewer_jupyter', __name__)
blueprint.add_url_rule('/preview/ipynb/<int:attachment_id>', 'preview_ipynb', RHEventPreviewIPyNB)
