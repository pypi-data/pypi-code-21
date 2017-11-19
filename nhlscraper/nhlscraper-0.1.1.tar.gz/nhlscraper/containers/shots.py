from typing import List

from nhlscrapi.games.events import EventType
from nhlscrapi.games.playbyplay import Play

from filters import old_filter, play_event_type_filter

class ShotsContainer:
    def __init__(self, game):
        self.game = game

    def shots(self):
        if not (hasattr(self, '_shots') and self._shots):
            self._shots = {
                'shots': self.shots_by_type_with_participants(EventType.Shot),
                'misses': self.shots_by_type_with_participants(EventType.Miss),
                'blocks': self.shots_by_type_with_participants(EventType.Block),
            }

        return self._shots

    def shots_by_type_with_participants(self, shot_type):
        all_plays = self.game.scrapi_game.plays
        shots = old_filter(play_event_type_filter(shot_type), all_plays)

        for shot in shots:
            event_type: str = str(shot.event)
            if event_type == 'Block':
                shot.shot_taker, shot.blocker = self._blocked_shot_participants(shot)
            elif event_type == 'Miss':
                shot.shot_taker, = self._missed_shot_participants(shot)
            else:
                shot.shot_taker, shot.goalie = self._shot_participants(shot)

            if not shot.json:
                shot.for_team, shot.against_team = self._shot_teams(shot)

        return shots

    def _shot_participants(self, shot: Play):
        participants: List[List[dict]] = self.game.event_participants(shot, ('shooter', 'goalie'))
        shooter_json: dict = participants['shooter'][0]
        goalie_json: dict = participants['goalie'][0] if len(participants['goalie']) else None

        shot_taker: dict = self.game.onice_json_from_scrapi(None, (shooter_json['fullName'],))

        if goalie_json:
            goalie: dict = self.game.onice_json_from_scrapi(None, (goalie_json['fullName'],))
        else:
            goalie = None

        return shot_taker, goalie

    def _blocked_shot_participants(self, shot: Play):
        participants: List[List[dict]] = self.game.event_participants(shot, ('shooter', 'blocker'))

        shooter_json: dict = participants['shooter'][0]
        blocker_json: dict = participants['blocker'][0]

        shot_taker: dict = self.game.onice_json_from_scrapi(None, (shooter_json['fullName'],))
        blocker: dict = self.game.onice_json_from_scrapi(None, (blocker_json['fullName'],))

        return shot_taker, blocker

    def _missed_shot_participants(self, shot: Play):
        participants: List[List[dict]] = self.game.event_participants(shot, ('shooter',))

        shooter_json: dict = participants['shooter'][0]
        shot_taker: dict = self.game.onice_json_from_scrapi(None, (shooter_json['fullName'],))

        return shot_taker,

    def _shot_teams(self, shot):
        for on_ice in shot.on_ice['home']:
            if on_ice['id'] == shot.shot_taker['id']:
                return self.game.teams['home'], self.game.teams['away']

        else:
            return self.game.teams['away'], self.game.teams['home']
