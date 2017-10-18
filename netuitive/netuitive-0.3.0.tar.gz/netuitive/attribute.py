
class Attribute(object):

    """
        A property or characteristic that is associated with Element

        :param name: Name of the attribute
        :type name: string
        :param value: Value of the attribute
        :type value: string
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value
