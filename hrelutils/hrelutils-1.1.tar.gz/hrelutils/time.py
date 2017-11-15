PERIOD_MINUTES = 20


def time_to_seconds(time):
    return (PERIOD_MINUTES-time.hour-1)*60 + (60-time.minute)
