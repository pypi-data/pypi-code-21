from typing import List

from nhlscrapi.games.events import EventType
from nhlscrapi.games.playbyplay import Play

from filters import old_filter, play_event_type_filter

class TurnoversContainer:
    def __init__(self, game):
        self.game = game

    def turnovers(self):
        if not (hasattr(self, '_turnovers') and self._turnovers):
            self._turnovers = {
                'giveaways': self.turnovers_by_type_with_participants(EventType.Giveaway),
                'takeaways': self.turnovers_by_type_with_participants(EventType.Takeaway),
            }

        return self._turnovers

    def turnovers_by_type_with_participants(self, turnover_type):
        all_plays = self.game.scrapi_game.plays
        turnovers = old_filter(play_event_type_filter(turnover_type), all_plays)

        for turnover in turnovers:
            if turnover_type == EventType.Giveaway:
                turnover.giver, = self._giveaway_participants(turnover)
            else:
                turnover.taker, = self._takeaway_participants(turnover)

            if not turnover.json:
                turnover.for_team, turnover.against_team = self._turnover_teams(turnover)

        return turnovers

    def _giveaway_participants(self, turnover: Play):
        participants: List[List[dict]] = self.game.event_participants(turnover, ('playerid',))
        player_json: dict = participants['playerid'][0]

        player: dict = self.game.onice_json_from_scrapi(None, (player_json['fullName'],))

        return player,

    def _takeaway_participants(self, turnover: Play):
        participants: List[List[dict]] = self.game.event_participants(turnover, ('playerid',))
        player_json: dict = participants['playerid'][0]

        player: dict = self.game.onice_json_from_scrapi(None, (player_json['fullName'],))

        return player,

    def _turnover_teams(self, turnover):
        for on_ice in turnover.on_ice['home']:
            if hasattr(turnover, 'giver') and on_ice['id'] == turnover.giver['id']:
                return self.game.teams['home'], self.game.teams['away']

            elif hasattr(turnover, 'taker') and on_ice['id'] == turnover.taker['id']:
                return self.game.teams['home'], self.game.teams['away']

        else:
            return self.game.teams['away'], self.game.teams['home']
