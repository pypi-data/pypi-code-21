"""This is a programme compiling with Head First Python Chapter 5"""


def get_coach_data(name_list):
    """The first parameter "name_list" determines whose data to process, which prints the least three different time."""

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

    for name in name_list:
        try:
            with open(name + ".txt") as file:
                data = file.readline()
                name = data.strip().split(",")
                name = sorted(set([sanitize(time) for time in name]))
        except IOError as err:
            print("File error: " + str(err))
        print(name[0:3])
