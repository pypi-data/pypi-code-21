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

def fuzzy (key, input, ref):
    fuzzy = {
        'future': {
            '10': 'imminently',
            '60': 'in {} seconds'.format(input),
            '120': 'in a minute',
            '1500': 'in {} minutes'.format(input/60),
            '2100': 'in a half hour',
            '3600': 'in {} minutes'.format(input/60),
            '7200': 'in an hour',
            '86400': 'in {} hours'.format(input/3600),            
            '2': 'tomorrow',
            '7': 'in {} days'.format(input),
            '14': 'in a week',
            '30': 'in {} weeks'.format(input/7),
            '60': 'in a month',
            '365': 'in {} months'.format(input/30),
            '730': 'in a year',
            '3649': 'in {} years'.format(input/365),
            '4015': 'in a decade',
            '36499':'in {} years'.format(input/365),
            '36865':'in a century',
            'inf':'in {} years'.format(input/365)
        },
        'past':{
            '10': 'just now',
            '60': '{} seconds ago'.format(input),
            '120': 'a minute ago',
            '1500': '{} minutes ago'.format(input/60),
            '2100': 'a half hour ago',
            '3600': '{} minutes ago'.format(input/60),
            '7200': 'an hour ago',
            '86400': '{} hours ago'.format(input/3600),
            '2': 'yesterday',
            '7': '{} days ago'.format(input),
            '14': 'a week ago',
            '30': '{} weeks ago'.format(input/7),
            '60': 'a month ago',
            '365': '{} months ago'.format(input/30),
            '730': 'a year ago',
            '3649': '{} years ago'.format(input/365),
            '4015': 'a decade ago',
            '36499':'{} years ago'.format(input/365),
            '36865':'a century ago',
            'inf':'{} years ago'.format(input/365)
        }
    }
    return fuzzy[ref][key]