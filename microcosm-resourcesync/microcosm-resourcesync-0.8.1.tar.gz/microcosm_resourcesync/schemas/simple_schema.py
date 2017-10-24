"""
A simplistic, non-HAL schema.

"""
from microcosm_resourcesync.following import FollowMode
from microcosm_resourcesync.schemas.base import Schema


class SimpleSchema(Schema):
    """
    A schema that encodes uri/type verbatim in its dictionary.

    """
    @property
    def embedded(self):
        return self.get("embedded", [])

    def links(self, follow_mode):
        if follow_mode == FollowMode.NONE:
            return []

        # no filtering by follow mode yet
        return self.get("links", [])

    @property
    def parents(self):
        return self.get("parents", [])

    @property
    def type(self):
        return self["type"]

    @property
    def uri(self):
        return self["uri"]
