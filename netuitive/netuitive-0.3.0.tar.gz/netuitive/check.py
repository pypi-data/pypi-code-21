
class Check(object):

    """
        A Check model
        :param name: Check name
        :type name: string
        :param elementId: Associated Element ID
        :type elementId: string
        :param interval: Check interval in seconds
        :type interval: int
    """

    def __init__(self,
                 name,
                 elementId,
                 interval):

        self.name = name
        self.elementId = elementId
        self.interval = interval
