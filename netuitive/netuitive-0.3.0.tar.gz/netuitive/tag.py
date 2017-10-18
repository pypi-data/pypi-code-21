
class Tag(object):

    """
        A label that is added to Element for grouping

        :param name: Name of the tag
        :type name: string
        :param value: Value of the tag
        :type value: string
    """

    def __init__(self, name, value=None):
        self.name = name
        self.value = value
