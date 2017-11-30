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


def get_coach_data2(name_list):
    """The first parameter "name_list" determines whose data to process, which prints the fastest three different times."""
    for each_name in name_list:
        try:
            with open(each_name + "2.txt") as file:
                data = file.readline().strip().split(",")
                name = dict()
                name["Name"] = data.pop(0)
                name["DOB"] = data.pop(0)
                name["Times"] = sorted(set([sanitize(time) for time in data]))[0:3]
                print(name["Name"] + "'s fastest three times are: " + str(name["Times"]))
        except IOError as err:
            print(err)
