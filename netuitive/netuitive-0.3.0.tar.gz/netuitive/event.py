import time
from .tag import Tag


class Event(object):
    """
        :param elementId: Element FQN
        :type elementId: string
        :param eventType: Type of event
        :type eventType: string
        :param title: Title of the event
        :type title: string
        :param message: The event message
        :type message: string
        :param level: One of [INFO, WARNING, CRITICAL]
        :type level: string
        :param tags: Tags for this event
        :type tags: list
        :param timestamp: Epoch timestamp of the event
        :type timestamp: int
        :param source: The source of the event
        :type source: string

        :Example: netuitive.Event('host01',
                        'INFO',
                        'test event',
                        'test message',
                        'INFO',
                        [['tag1',val1],['tag2',val2]],
                        1434110794,
                        'deployment')

    """

    def __init__(self,
                 elementId,
                 eventType,
                 title,
                 message,
                 level,
                 tags=None,
                 timestamp=None,
                 source=None):

        self.type = eventType.upper()
        self.title = title

        if source is not None:
            self.source = source

        if tags is not None:
            self.tags = []
            for t in tags:
                self.tags.append(Tag(t[0], t[1]))

        if timestamp is None:
            self.timestamp = int(time.mktime(time.gmtime())) * 1000
        else:
            self.timestamp = timestamp * 1000

        if (self.type == 'INFO' and
                message is not None and
                level is not None):

            self.data = EventType(elementId, 'INFO', message, level)


class EventType(object):

    """
        :param eventType: Type of the event
        :type source: string
        :param elementId: Element FQN
        :type elementId: string
        :param level: One of [INFO, WARNING, CRITICAL]
        :type level: string
        :param message: The event message
        :type message: string

    """

    def __init__(self, elementId, eventtype, message=None, level=None):
        self.elementId = elementId

        if (eventtype.upper() == 'INFO' and
                message is not None and
                level is not None):

            self.level = level
            self.message = message
