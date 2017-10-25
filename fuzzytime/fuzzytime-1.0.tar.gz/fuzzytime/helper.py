from datetime import datetime, date, time

#=================================================================
#~~~~~~~~~~~~~~~~~~~~~~~~ Helper Functions ~~~~~~~~~~~~~~~~~~~~~~~
#=================================================================

# Convert input into type datetime. This function handles datetime, date, time, int, float and str inputs
# Str inputs may contain dates separated by '/' or '-' ex. YYYY/MM/DD or YYYY-MM-DD. The time inputs must be
# separated by ':' ex. HH:MM:SS.
def convert (input):
    if isinstance(input, datetime):
        return input
    elif isinstance(input, date):
        return date_to_datetime(input)
    elif isinstance(input, time):
        return time_to_datetime(input)
    elif isinstance(input, (int, float)):
        return timestamp_to_datetime(input)
    elif isinstance(input, (str)):
        return string_to_datetime(input)
    else:
        return None

# Convert a date input into a datetime
def date_to_datetime (d):
    return combine(d, time(0, 0, 0))

# Convert a time input into a datetime
def time_to_datetime (t):
    return combine(date.today(), t)

# Combine a date and time into a whole datetime
def combine (d, t):
    if (d is not None) and (t is not None):
        return datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
    return None

# Convert a timestamp into a datetime
def timestamp_to_datetime (ts):
    return datetime.fromtimestamp(ts)

# Split a string into a datetime 
def string_to_datetime (dt_str):
    if dt_str:
        dt_str = dt_str.replace('/', '-')
        if ' ' in dt_str:
            dt = dt_str.split(' ')
            if len(dt) == 2:
                d = string_to_date(dt[0])
                t = string_to_time(dt[1])
                return combine(d, t)
        else:
            # In case the string contains only a date or time input
            if '-' in dt_str:
                return date_to_datetime(string_to_date(dt_str))
            elif ':' in dt_str:
                return time_to_datetime(string_to_time(dt_str))
    return None

# Split a string into a date
def string_to_date (d_str):
    if not d_str:
        return None
    try:
        d_arr = d_str.split('-')     
        return date(int(d_arr[0]), int(d_arr[1]), int(d_arr[2]))
    except:
        return None

# Split a string into a time
def string_to_time (t_str):
    if not t_str:
        return None
    try:
        t_arr = t_str.split(':')
        return time(int(t_arr[0]), int(t_arr[1]), int(t_arr[2]))
    except:
        return None