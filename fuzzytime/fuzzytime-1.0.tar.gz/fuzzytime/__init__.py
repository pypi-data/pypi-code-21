from datetime import datetime, date, time
from helper import * 

#=================================================================
#~~~~~~~~~~~~~~~~~~~~~~~~~ Main Functions ~~~~~~~~~~~~~~~~~~~~~~~~
#=================================================================

# Function returns a fuzzy timestamp statement for an inputted datetime. Example return statements include:
# "Just now", 'Yesterday", 'X seconds ago", 'Y minutes ago', 'Z years ago', etc...

def timeago (input = False):
    input = convert(input)
    now = convert(datetime.now())
    dif = now - input
    sec_dif = dif.seconds
    day_dif = dif.days

    # Quick return in case inputted time was in the future.
    if day_dif < 0:
        return ''

    # If a full day hasn't passed between now and the inputted time
    if day_dif == 0:
        if sec_dif < 10:
            return "just now"
        if sec_dif < 60:
            return str(sec_dif) + " seconds ago"
        if sec_dif < 120:
            return "a minute ago"
        if sec_dif < 2100 and sec_dif > 1500:
            return "a half-hour ago"
        if sec_dif < 3600:
            return str(sec_dif / 60) + " minutes ago"
        if sec_dif < 7200:
            return "an hour ago"
        if sec_dif < 86400:
            return str(sec_dif / 3600) + " hours ago"
    # More than a days time has passed.
    else:
        if day_dif == 1:
            return "Yesterday"
        if day_dif < 7:
            return str(day_dif) + " days ago"
        if day_dif < 14:
            return str(day_dif / 7) + " week ago"
        if day_dif < 30:
            return str(day_dif / 7) + " weeks ago"
        if day_dif < 60:
            return str(day_dif / 30) + " month ago"
        if day_dif < 365:
            return str(day_dif / 30) + " months ago"
        if day_dif < 730:
            return str(day_dif / 365) + " year ago"
        if day_dif < 4015 and day_dif > 3649:
            return "a decade ago"
        if day_dif < 36865 and day_dif > 36499:
            return "a century ago"
        return str(day_dif / 365) + " years ago"
        
# Function returns how many seconds ago the input datetime was
def secondsago (input = False):
    input = convert(input)
    now = convert(datetime.now())
    dif = now - input
    sec_dif = dif.seconds
    day_dif = dif.days
    return str(day_dif * 86400 + sec_dif) + " seconds ago"

# Function returns how many minutes ago the input datetime was 
def minutesago (input = False):
    input = convert(input)
    now = convert(datetime.now())
    dif = now - input
    sec_dif = dif.seconds
    day_dif = dif.days
    return str((day_dif * 86400 + sec_dif) / 60) + " minutes ago"

# Function returns a future fuzzy timestamp statement for an inputted datetime. Example return statements include:
# "Just now", 'Tomorrow", 'in X seconds", 'in Y minutes', 'in Z years', etc...
def timeahead (input = False):
    input = convert(input)
    now = convert(datetime.now())
    dif = input - now
    sec_dif = dif.seconds
    day_dif = dif.days

    # Quick return in case inputted time was in the past.
    if day_dif < 0:
        return ''

    # If a full day hasn't passed between now and the inputted time
    if day_dif == 0:
        if sec_dif < 10:
            return "just now"
        if sec_dif < 60:
            return "in " + str(sec_dif) + " seconds"
        if sec_dif < 120:
            return "in a minute"
        if sec_dif < 2100 and sec_dif > 1500:
            return "in a half-hour"
        if sec_dif < 3600:
            return "in " + str(sec_dif / 60) + " minutes"
        if sec_dif < 7200:
            return "an hour"
        if sec_dif < 86400:
            return "in " + str(sec_dif / 3600) + " hours"
    # More than a days time has passed.
    else:
        if day_dif == 1:
            return "Tomorrow"
        if day_dif < 7:
            return "in " + str(day_dif) + " days"
        if day_dif < 14:
            return "in " + str(day_dif / 7) + " week"
        if day_dif < 30:
            return "in " + str(day_dif / 7) + " weeks"
        if day_dif < 60:
            return "in " + str(day_dif / 30) + " month"
        if day_dif < 365:
            return "in " + str(day_dif / 30) + " months"
        if day_dif < 730:
            return "in " + str(day_dif / 365) + " year"
        if day_dif < 4015 and day_dif > 3649:
            return "a decade"
        if day_dif < 36865 and day_dif > 36499:
            return "in a century"
        return "in " + str(day_dif / 365) + " years"

# Evaluates the input and calls the appropriate timeago() or timeahead() function
def fuzzytime (input = False):
    input = convert(input)
    now = convert(datetime.now())
    dif = now - input
    sec_dif = dif.seconds
    day_dif = dif.days
    if day_dif < 0:
        return timeahead(input)
    else:
        return timeago(input)