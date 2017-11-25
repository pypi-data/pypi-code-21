from datetime import datetime
from dateutil.parser import parse
from dateutil.parser import parserinfo


class CustomParse(parserinfo):
    def __init__(self):
        self.JUMP.append(":")
        super(CustomParse, self).__init__()


def parseline(line):
    """ Try to parse a time from the beginning of this line. If cannot then return unix epoch. """
    words = []
    time = None

    # Try to parse from the first word
    for word in line.split():
        words.append(word.strip('[]'))
        try:
            time = parse(' '.join(words), parserinfo=CustomParse()).replace(tzinfo=None)
        except ValueError:
            if time is not None:
                break
            words.pop()

    if time is None:
        return datetime(1970, 1, 1, 0, 0)

    return time
