from nhlscrapi.games.events import EventType
from nhlscrapi.games.playbyplay import Play

from nhlscraper import filters

class GoalsContainer:
    def __init__(self, game):
        self.game = game

    def goals(self):
        if not (hasattr(self, '_goals') and self._goals):
            all_plays = self.game.scrapi_game.plays
            self._goals = list(filter(filters.play_event_type_filter(EventType.Goal), all_plays))

            for goal in self._goals:
                goal.shot_taker, goal.assists, goal.goalie = self._goal_participants(goal)

                if not goal.json:
                    goal.for_team, goal.against_team = self._goal_teams(goal)

        return self._goals

    def _goal_participants(self, goal):
        assert isinstance(goal, Play)
        assert goal.event.event_type == EventType.Goal

        participants = self.game.event_participants(goal, ('scorer', 'goalie', 'assist'))

        shooter_json = participants['scorer'][0]
        goalie_json = participants['goalie'][0] if len(participants['goalie']) else None
        assists_json = participants['assist']

        if shooter_json:
            shooter = self.game.onice_json_from_scrapi(None, (shooter_json['fullName'],))
        else:
            shooter = None

        if goalie_json:
            goalie = self.game.onice_json_from_scrapi(None, (goalie_json['fullName'],))
        else:
            goalie = None

        assists = [self.game.onice_json_from_scrapi(None, (assist_json['fullName'],)) for assist_json in assists_json]

        return shooter, assists, goalie

    def _goal_teams(self, goal):
        for on_ice in goal.on_ice['home']:
            if on_ice['id'] == goal.shot_taker['id']:
                return self.game.teams['home'], self.game.teams['away']

        else:
            return self.game.teams['away'], self.game.teams['home']
