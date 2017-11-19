from nhlscrapi.games.events import EventType
from nhlscrapi.games.playbyplay import Play

import filters

class HitsContainer:
    def __init__(self, game):
        self.game = game

    def hits(self):
        if not (hasattr(self, '_hits') and self._hits):
            all_plays = self.game.scrapi_game.plays
            self._hits = list(filter(filters.play_event_type_filter(EventType.Hit), all_plays))

            for hit in self._hits:
                hit.hitter, hit.hittee = self._hit_participants(hit)

                if not hit.json:
                    hit.for_team, hit.against_team = self._hit_teams(hit)

        return self._hits

    def _hit_participants(self, hit):
        assert isinstance(hit, Play)
        assert hit.event.event_type == EventType.Hit

        participants = self.game.event_participants(hit, ('hitter', 'hittee'))

        hitter_json = participants['hitter'][0] if len(participants['hitter']) else None
        hittee_json = participants['hittee'][0] if len(participants['hittee']) else None

        if hitter_json:
            assert 'fullName' in hitter_json
            hitter = self.game.onice_json_from_scrapi(None, (hitter_json['fullName'],))
        else:
            hitter = None

        if hittee_json:
            assert 'fullName' in hittee_json
            hittee = self.game.onice_json_from_scrapi(None, (hittee_json['fullName'],))
        else:
            hittee = None

        return hitter, hittee

    def _hit_teams(self, hit):
        for on_ice in hit.on_ice['home']:
            if hit.hitter and on_ice['id'] == hit.hitter['id']:
                return self.game.teams['home'], self.game.teams['away']
            elif hit.hittee and on_ice['id'] == hit.hittee['id']:
                return self.game.teams['away'], self.game.teams['home']

        else:
            return self.game.teams['away'], self.game.teams['home']
