"""
A collection of serializers that can operate on dict types. plumb
implementations can optionally use these serializers.
"""

import json


class JSON:
    """Provide serialize() and deserialize() methods to deal with JSON."""

    def serialize(self, pkg):
        """Return a string representation of the data."""
        return json.dumps(pkg)

    def deserialize(self, msg):
        """Return a dict from the JSON string."""
        return json.loads(msg)
