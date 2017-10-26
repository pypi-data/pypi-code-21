from datetime import datetime, date, time
from helper import * 

#=================================================================
#~~~~~~~~~~~~~~~~~~~~~~~~~ Main Functions ~~~~~~~~~~~~~~~~~~~~~~~~
#=================================================================

# Function returns a fuzzy timestamp statement for an inputted datetime in the past or future. 
# Example return statements include:"Just now", 'Yesterday", 'X seconds ago", 'in Y minutes', 
# 'in a year', etc...

def fuzzytime (input = False):
    input = convert(input)
    now = convert(datetime.now())
    ref = 'future'
    if (now - input).days < 0:
        dif = input - now
    else:
        ref = 'past'
        dif = now - input

    sec_dif = dif.seconds
    day_dif = dif.days
    
    if day_dif == 0:
        arr = [0, 10, 60, 120, 1500, 2100, 3600, 7200, 86400]
        check = sec_dif
        e = len(arr) - 1
    else:
        arr = [0, 2, 7, 14, 30, 61, 365, 730, 3649, 4015, 36499, 36865, float('inf')]
        check = day_dif
        e = len(arr) - 1

    s = 0
    while s != e-1:
        m = (s+e)/2
        if (arr[m] <= check):
            s = m
        elif (arr[m] > check):
            e = m

    return fuzzy(str(arr[e]), check, ref)
        
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

        