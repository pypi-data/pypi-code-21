from typing import List

from nhlscrapi.games.events import EventType
from nhlscrapi.games.playbyplay import Play

class ShootoutContainer:
    def __init__(self, game):
        self.game = game

    def shootout(self):
        if not (hasattr(self, '_shootout') and self._shootout):
            shootout_events = filter(is_shootout_event, self.game.scrapi_game.plays)
            for shootout_event in shootout_events:
                shootout_event.shot_taker, shootout_event.goalie = self._shootout_participants(shootout_event)

                if not shootout_event.json:
                    shootout_event.for_team, shootout_event.against_team = self._shootout_teams(shootout_event)

    def _shootout_participants(self, shootout: Play):
        participants: List[List[dict]] = self.game.event_participants(shootout, ('shooter', 'goalie'))
        shooter_json: dict = participants['shooter'][0]
        goalie_json: dict = participants['goalie'][0] if len(participants['goalie']) else None

        shot_taker: dict = self.game.onice_json_from_scrapi(None, (shooter_json['fullName'],))

        if goalie_json:
            goalie: dict = self.game.onice_json_from_scrapi(None, (goalie_json['fullName'],))
        else:
            goalie = None

        return shot_taker, goalie

    def _shootout_teams(self, shootout):
        for on_ice in shootout.on_ice['home']:
            if on_ice['id'] == shootout.goalie['id']:
                return self.game.teams['away'], self.game.teams['home']

        else:
            return self.game.teams['home'], self.game.teams['away']

def is_shootout_event(event):
    return event.event.event_type_str in ('ShootOutAtt', 'ShootOutGoal')
