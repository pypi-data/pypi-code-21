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


class Athlete:
    def __init__(self, name, dob=None, times=None):
        # The code to initialize a "Athlete" object.
        self.name = name
        self.dob = dob
        self.times = times

    def top(self, index=3):
        # The code to return fastest time(s), the parameter "index" defines how many fastest times you want to return.
        if index > len(self.times):
            print("Index exceeds!")
            return
        else:
            return sorted(set([sanitize(time) for time in self.times]))[0:index]


def get_coach_data2(filename):
    try:
        with open(filename) as f:
            data = f.readline()
            templ = data.strip().split(",")
            return Athlete(templ.pop(0), templ.pop(0), templ)
    except IOError as err:
        print("File error: " + str(err))
        return
