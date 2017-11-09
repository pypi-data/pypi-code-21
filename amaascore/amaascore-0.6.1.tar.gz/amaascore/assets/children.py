from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.core.amaas_model import AMaaSModel


class Link(AMaaSModel):

    def __init__(self, linked_asset_id, *args, **kwargs):
        self.linked_asset_id = linked_asset_id
        super(Link, self).__init__(*args, **kwargs)
