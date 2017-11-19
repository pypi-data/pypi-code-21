import re

from nhlscrapi.games.playbyplay import Play

import gametime

def old_filter(f, iter):
    return list(filter(f, iter))

def json_play_match(play):
    assert hasattr(play, 'time')

    def json_match(play_json):
        assert 'about' in play_json
        assert 'periodTime' in play_json['about']
        assert re.match('\d+:\d+', play_json['about']['periodTime'])

        play_time = gametime.period_time(play.time)

        json_min, json_sec = list(map(int, play_json['about']['periodTime'].split(':')))
        json_time = gametime.period_time({ 'min': json_min, 'sec': json_sec })

        return play_time == json_time and play.period == play_json['about']['period']

    return json_match

def play_event_type_filter(event_type):
    def event_type_match(play):
        assert isinstance(play, Play)

        return play.event.event_type == event_type

    return event_type_match

def json_event_type_filter(event_type):
    def event_type_match(event):
        assert isinstance(event, dict)

        return event['result']['event'].upper() == event_type

    return event_type_match

def player_type_match(player_type):
    assert isinstance(player_type, str)

    def match_check(player):
        return player['playerType'].lower() == player_type.lower()

    return match_check
