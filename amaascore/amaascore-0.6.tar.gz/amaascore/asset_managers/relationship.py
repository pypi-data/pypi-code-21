from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.core.amaas_model import AMaaSModel
from amaascore.asset_managers.enums import RELATIONSHIP_TYPES


class Relationship(AMaaSModel):

    def __init__(self, asset_manager_id, related_id, relationship_id,  relationship_type, client_id,
                 relationship_status='Pending', *args, **kwargs):
        """

        :param asset_manager_id: The ID of the Asset Manager who owns this relationship
        :param related_id: The ID of the Asset Manager to whom this relationship connects
        :param relationship_id: An ID for this relationship
        :param relationship_type: The type of relationship between these Asset Managers
        :param client_id: The client_id that owns this relationship
        :param relationship_status: The status of the relationship
        :param args:
        :param kwargs:
        """
        self.asset_manager_id = asset_manager_id
        self.related_id = related_id
        self.relationship_id = relationship_id
        self.relationship_status = relationship_status
        self.relationship_type = relationship_type
        self.client_id = client_id
        super(Relationship, self).__init__(*args, **kwargs)

    @property
    def relationship_type(self):
        if hasattr(self, '_relationship_type'):
            return self._relationship_type

    @relationship_type.setter
    def relationship_type(self, relationship_type):
        if relationship_type:
            if relationship_type not in RELATIONSHIP_TYPES:
                raise ValueError("Invalid Relationship Type: %s" % relationship_type)
            else:
                self._relationship_type= relationship_type
