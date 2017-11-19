from nhlscrapi.games.events import EventType
from nhlscrapi.games.playbyplay import Play

import filters

class PenaltiesContainer:
    def __init__(self, game):
        self.game = game

    def penalties(self):
        if not (hasattr(self, '_penalties') and self._penalties):
            all_plays = self.game.scrapi_game.plays
            self._penalties = list(filter(filters.play_event_type_filter(EventType.Penalty), all_plays))

            for penalty in self._penalties:
                penalty.offender, penalty.drawer, penalty.server = self._penalty_participants(penalty)

                if not penalty.json:
                    penalty.for_team, penalty.against_team = self._penalty_teams(penalty)

        return self._penalties

    def _penalty_participants(self, penalty):
        assert isinstance(penalty, Play)
        assert penalty.event.event_type == EventType.Penalty

        participants = self.game.event_participants(penalty, ('penaltyon', 'drewby', 'servedby'))

        offender_json = participants['penaltyon'][0] if len(participants['drewby']) else None
        drawer_json = participants['drewby'][0] if len(participants['drewby']) else None

        if offender_json:
            offender = self.game.onice_json_from_scrapi(None, (offender_json['fullName'],))
        else:
            offender = None

        if drawer_json:
            drawer = self.game.onice_json_from_scrapi(None, (drawer_json['fullName'],))
        else:
            drawer = None

        if participants['servedby']:
            server = self.game.onice_json_from_scrapi(None, (participants['servedby'][0]['fullName'],))
        else:
            server = None

        return offender, drawer, server

    def _penalty_teams(self, penalty):
        for on_ice in penalty.on_ice['home']:
            if penalty.offender and on_ice['id'] == penalty.offender['id']:
                return self.game.teams['home'], self.game.teams['away']
            elif penalty.server and on_ice['id'] == penalty.server['id']:
                return self.game.teams['home'], self.game.teams['away']

        else:
            return self.game.teams['away'], self.game.teams['home']
