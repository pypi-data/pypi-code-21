"""KB feature resource."""
from __future__ import absolute_import, division, print_function, unicode_literals

from ..base import BaseResource


class Feature(BaseResource):
    """Knowledge base Feature resource."""

    endpoint = 'kb.feature.admin'
    query_endpoint = 'kb.feature.search'
    query_method = 'POST'

    WRITABLE_FIELDS = ('source', 'feature_id', 'species', 'type', 'sub_type', 'name',
                       'full_name', 'description', 'aliases')
    UPDATE_PROTECTED_FIELDS = ('source', 'feature_id')
    READ_ONLY_FIELDS = ('id',)

    def __repr__(self):
        """Format feature representation."""
        # pylint: disable=no-member
        return "<Feature source='{}' feature_id='{}'>".format(self.source, self.feature_id)
