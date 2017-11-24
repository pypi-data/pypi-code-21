from datetime import datetime
from dateutil.parser import parse


def parseline(line):
    """ Try to parse a time from the beginning of this line. If cannot then return unix epoch. """
    words = []
    time = None

    for word in line.split():
        words.append(word.translate(None, '[]{}<>|()*'))
        try:
            time = parse(' '.join(words))
        except ValueError:
            break

    if time is None:
        return datetime(1970, 1, 1, 0, 0)

    return time
