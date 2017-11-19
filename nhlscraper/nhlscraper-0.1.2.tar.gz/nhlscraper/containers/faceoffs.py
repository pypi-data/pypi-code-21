from nhlscrapi.games.events import EventType
from nhlscrapi.games.playbyplay import Play

import filters

class FaceoffsContainer:
    def __init__(self, game):
        self.game = game

    def faceoffs(self):
        if not (hasattr(self, '_faceoffs') and self._faceoffs):
            all_plays = self.game.scrapi_game.plays
            self._faceoffs = [play for play in all_plays if play.event.event_type == EventType.FaceOff]

            assert isinstance(self._faceoffs, list)
            assert len(self._faceoffs), 'No faceoffs'

            for faceoff in self._faceoffs:
                faceoff.winner, faceoff.loser = self._faceoff_participants(faceoff)

                if not faceoff.json: # no for_team or against_team:
                    faceoff.for_team, faceoff.against_team = self._faceoff_teams(faceoff)


        return self._faceoffs

    def _faceoff_participants(self, faceoff):
        assert isinstance(faceoff, Play)
        assert faceoff.event.event_type == EventType.FaceOff

        participants = self.game.event_participants(faceoff, ('winner', 'loser'))

        winner_json = participants['winner'][0]
        loser_json = participants['loser'][0]

        assert 'fullName' in winner_json
        assert 'fullName' in loser_json

        winner = self.game.onice_json_from_scrapi(None, [winner_json['fullName']])
        loser = self.game.onice_json_from_scrapi(None, [loser_json['fullName']])

        return winner, loser


    def _faceoff_teams(self, faceoff):
        for on_ice in faceoff.on_ice['home']:
            if on_ice['id'] == faceoff.winner['id']:
                return self.game.teams['home'], self.game.teams['away']

        else:
            return self.game.teams['away'], self.game.teams['home']
