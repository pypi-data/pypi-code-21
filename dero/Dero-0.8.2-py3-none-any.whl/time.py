
import math, time, datetime, timeit

def time_elapsed(seconds):
    '''
    Takes an amount of time in seconds and converts it into how a human would say it. 
    
    Required Options:
    seconds: time in number of seconds (raw number, int or float). 
    
    ''' 
    if seconds > 60: #if this is greater than a minute
        if seconds > 60 * 60: #if this is greater than an hour
            if seconds > 60 * 60 * 24: #if this is greater than a day
                if seconds > 60 * 60 * 24 * 30: #if this is greater than a month (approx.):
                    months = math.trunc(seconds / (60 * 60 * 24 *30))
                    seconds -= months * (60 * 60 * 24 * 30)
                    days = math.trunc(seconds / (60 * 60 * 24))
                    seconds -= days * (60 * 60 * 24)
                    hours = math.trunc(seconds / (60 * 60))
                    seconds -= hours * (60 * 60)
                    minutes = math.trunc(seconds / 60)
                    seconds -= minutes * 60
                    seconds = math.trunc(seconds)
                    print("Operation took {} months, {} days, {} hours, {} minutes, and {} seconds.".format(months, days, hours, minutes, seconds))
                else:
                    days = math.trunc(seconds / (60 * 60 * 24))
                    seconds -= days * (60 * 60 * 24)
                    hours = math.trunc(seconds / (60 * 60))
                    seconds -= hours * (60 * 60)
                    minutes = math.trunc(seconds / 60)
                    seconds -= minutes * 60
                    seconds = math.trunc(seconds)
                    print("Operation took {} days, {} hours, {} minutes, and {} seconds.".format(days, hours, minutes, seconds))
            else: #if this is greater than an hour but less than a day
                hours = math.trunc(seconds / (60 * 60))
                seconds -= hours * (60 * 60)
                minutes = math.trunc(seconds / 60)
                seconds -= minutes * 60
                seconds = math.trunc(seconds)
                print("Operation took {} hours, {} minutes, and {} seconds.".format(hours, minutes, seconds))
        else: #if this is greater than a minute but less than an hour
            minutes = math.trunc(seconds / 60)
            seconds -= minutes * 60
            seconds = math.trunc(seconds)
            print("Operation took {} minutes and {} seconds.".format(minutes, seconds))
    else: #if this is less than a minute
        seconds = math.trunc(seconds)
        print("Operation took {} seconds.".format(seconds))
        
def estimate_time(length,i,start_time,output=True):
    '''
    Returns the estimate of when a looping operation will be finished. 
    
    HOW TO USE:
    This function goes at the end of the loop to be timed. Outside of this function at the beginning of the
    loop, you must start a timer object as follows:
    
    start_time = timeit.default_timer()
    
    So the entire loop will look like this:
    
    my_start_time = timeit.default_timer()
    for i, item in enumerate(my_list):
    
        #Do loop stuff here
        
         estimate_time(len(my_list),i,my_start_time)
         
    REQUIRED OPTIONS:
    length:     total number of iterations for the loop
    i:          iterator for the loop
    start_time: timer object, to be started outside of this function (SEE ABOVE)
    
    OPTIONAL OPTIONS:
    output: specify other than True to suppress printing estimated time. Use this if you want to just store the time
            for some other use or custom output. The syntax then is as follows:
    
    my_start_time = timeit.default_timer()
    for i, item in enumerate(my_list):
        
        #Do loop stuff here
        
        my_timer = estimate_time(len(my_list),i,my_start_time)
        print("I like my output sentence better! Here's the estimate: {}".format(my_timer))
    
    '''
    avg_time = (timeit.default_timer() - start_time)/(i + 1)
    loops_left = length - (i + 1)
    est_time_remaining = avg_time * loops_left
    est_finish_time = datetime.datetime.now() + datetime.timedelta(0,est_time_remaining)
    
    if output == True:
        print("Estimated finish time: {}. Completed {}/{}, ({:.0%})".format(est_finish_time, i, length, i/length), end="\r")
    
    return est_finish_time

def increment_dates(start_date,end_date,frequency='a'):
    '''
    Returns a list of dates inbetween start and end dates. start_date and end_date should be in one of the following
    date formats:
        mm/dd/yyyy, mm/yyyy, yyyy
    Dates should be frequency should be a single letter, 'a' for annual, 'm' for monthly, 'w' for weekly, and 'd' for daily
    '''
    #Find number of slashes to determine how to parse date
    number_of_slashes = []
    number_of_slashes.append(start_date.count('/'))
    number_of_slashes.append(end_date.count('/'))
    date_formats = ['%Y','%Y'] #set container for date formats
    
    for i, number in enumerate(number_of_slashes):
        if number == 0: #no slashes means interpret as year
            pass #already set as year in container
        if number == 1: #one slash means interpret as month/year
            date_formats[i] = '%m/%Y'
        if number == 2: #one slash means interpret as month/year
            date_formats[i] = '%m/%d/%Y'
    
    start = datetime.datetime.strptime(start_date, date_formats[0]).date()
    end   = datetime.datetime.strptime(end_date,   date_formats[1]).date()
    delta = end - start
    
    number_of_years = end.year - start.year
    number_of_months = end.month - start.month
    number_of_days = end.day - start.day
    
    if frequency == 'd': number_of_periods = delta.days + 1 
    if frequency == 'w': number_of_periods = math.ceil((delta.days + 1)/7) 
    if frequency == 'a': number_of_periods = math.ceil((delta.days + 1)/365)
    if frequency == 'm': number_of_periods = math.ceil((delta.days + 1)/(365/12))
    
    outlist = []
    for period in range(number_of_periods):
        if frequency == 'd': 
            new_date = start + datetime.timedelta(days=period)
            outlist.append(str(new_date.month) + '/' + str(new_date.day) + '/' + str(new_date.year))
        if frequency == 'w': 
            new_date = start + datetime.timedelta(weeks=period)
            outlist.append(str(new_date.month) + '/' + str(new_date.day) + '/' + str(new_date.year))
        if frequency == 'a': outlist.append(start.year + period)
        if frequency == 'm':
            new_period = period - 1
            current_month = (start.month + new_period)
            current_year = start.year
            years_passed = math.floor(current_month/12)
            current_year += years_passed
            current_month -= 12 * years_passed - 1
            if current_month > 12:
                pass
            outlist.append(str(current_month) + '/' + str(current_year))
    
    return outlist