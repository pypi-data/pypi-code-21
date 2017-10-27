"""KB mapping resource."""
from __future__ import absolute_import, division, print_function, unicode_literals

from ..base import BaseResource


class Mapping(BaseResource):
    """Knowledge base Mapping resource."""

    endpoint = 'kb.mapping.admin'
    query_endpoint = 'kb.mapping.search'
    query_method = 'POST'

    WRITABLE_FIELDS = ()
    UPDATE_PROTECTED_FIELDS = ()
    READ_ONLY_FIELDS = ('id', 'relation_type', 'source_db', 'source_id', 'target_db', 'target_id')

    def __repr__(self):
        """Format mapping representation."""
        # pylint: disable=no-member
        return "<Mapping source_db='{}' source_id='{}' target_db='{}' target_id='{}'>".format(
            self.source_db, self.source_id, self.target_db, self.target_id)
