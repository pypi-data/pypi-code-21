import re

def game_time(period, time):
    return (int(period)-1)*60*20 + period_time(time)

def period_time(time):
    if isinstance(time, dict):
        assert 'min' in time
        assert 'sec' in time

        return time['min'] * 60 + time['sec']

    elif isinstance(time, str):
        minutes, seconds = re.findall('(\d+):(\d+)', str(time))[0]
        return int(minutes)*60 + int(seconds)


