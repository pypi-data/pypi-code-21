"""This is a programme compiling with Head First Python Chapter 6"""


def sanitize(time):
    """Uniforming time types."""

    if "-" in time:
        splitter = "-"
    elif ":" in time:
        splitter = ":"
    else:
        return time
    (mins, secs) = time.split(splitter)
    return mins + "." + secs


class AthleteList(list):
    def __init__(self, name, dob=None, times=[]):
        list.__init__([])
        self.name = name
        self.dob = dob
        self.extend(times)

    def top(self, index=3):
        # The code to return fastest time(s), the parameter "index" defines how many fastest times you want to return.
        return sorted(set([sanitize(time) for time in self]))[0:index]


def get_coach_data2(filename):
    try:
        with open(filename) as f:
            data = f.readline().strip().split(",")
            return AthleteList(data.pop(0), data.pop(0), data)
    except IOError as err:
        print("File error: " + str(err))
        return
