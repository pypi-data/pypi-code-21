class Module(object):
    """Base class for Stride app modules."""

    type = None

    def __init__(self, key):
        self.properties = {}
        self.properties['key'] = key

    def add_property(self, property, value):
        self.properties[property] = value

    def to_descriptor(self):
        """Output app descriptor data as a dict."""
        return self.properties
