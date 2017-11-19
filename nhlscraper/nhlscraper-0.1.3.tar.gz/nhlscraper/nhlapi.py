import requests

from . import filters

#SSSSGGGGGG
LIVE_URL = 'https://statsapi.web.nhl.com/api/v1/game/{season}{game}/feed/live?site=en_nhl'

FACEOFF = 'FACEOFF'
HIT = 'HIT'
GOAL = 'GOAL'
SHOT = 'SHOT'
MISSED_SHOT = 'MISSED SHOT'
BLOCKED_SHOT = 'BLOCKED SHOT'
GIVEAWAY = 'GIVEAWAY'
TAKEAWAY = 'TAKEAWAY'
PENALTY = 'PENALTY'

class NhlApi():
    def __init__(self, season, game, json={}):
        self.season = season
        self.game = game
        self._live_json = json

    def live_json(self):
        if not (hasattr(self, '_live_json') and self._live_json):
            live_url = self.format_url(LIVE_URL)
            live_data_request = requests.get(live_url)

            self._live_json = live_data_request.json()

        return self._live_json

    def pbp_json(self):
        return self.live_json()['liveData']['plays']['allPlays']

    def faceoffs_json(self):
        if not (hasattr(self, '_faceoffs_json') and self._faceoffs_json):
            self._faceoffs_json = list(self.filter_events_by_type(FACEOFF))

        return self._faceoffs_json

    def hits_json(self):
        if not (hasattr(self, '_hits_json') and self._hits_json):
            self._hits_json = self.filter_events_by_type(HIT)

        return self._hits_json

    def goals_json(self):
        if not (hasattr(self, '_goals_json') and self._goals_json):
            self._goals_json = self.filter_events_by_type(GOAL)

        return self._goals_json

    def shots_json(self):
        if not (hasattr(self, '_shots_json') and self._shots_json):
            self._shots_json = self.filter_events_by_type(SHOT)

        return self._shots_json

    def misses_json(self):
        if not (hasattr(self, '_misses_json') and self._misses_json):
            self._misses_json = self.filter_events_by_type(MISSED_SHOT)

        return self._misses_json

    def blocks_json(self):
        if not (hasattr(self, '_blocks_json') and self._blocks_json):
            self._blocks_json = self.filter_events_by_type(BLOCKED_SHOT)

        return self._blocks_json

    def giveaways_json(self):
        if not (hasattr(self, '_giveaways_json') and self._giveaways_json):
            self._giveaways_json = self.filter_events_by_type(GIVEAWAY)

        return self._giveaways_json

    def takeaways_json(self):
        if not (hasattr(self, '_takeaways_json') and self._takeaways_json):
            self._takeaways_json = self.filter_events_by_type(TAKEAWAY)

        return self._takeaways_json

    def penalties_json(self):
        if not (hasattr(self, '_penalties_json') and self._penalties_json):
            self._penalties_json = self.filter_events_by_type(PENALTY)

        return self._penalties_json

    # This isn't actually very good because the team information is wildly useless
    def players_json(self):
        return self.live_json()['gameData']['players']

    def format_url(self, url, old_style=False):
        six_digit_game = str(self.game).zfill(6)

        formatted_season = str(self.season)
        if old_style: # eg: 20152016
            formatted_season += str(self.season+1)

        return url.format(season=formatted_season, game=six_digit_game)

    def filter_events_by_type(self, event_type):
        return list(filter(filters.json_event_type_filter(event_type), self.pbp_json()))
