from typing import List

from nhlscraper import GameContainer
from utilities import iterator_nonempty

from nhlscrapi.games import events, playbyplay

test_games = (
    # (2016, 20001),
    # (2014, 20010),
    # (2010, 20123), # 2010 is the earliest we can go back with the JSON method for faceoffs
    # # I'm assuming they have JSON rosters going back, though. Should be able to cross reference
    # (2016, 30414),
    # (2016, 20021),
     (2016, 20047),
    (2016, 20046),
    (2016, 20049),
    (2016, 20070),
    (2007, 20008),
    (2016, 21216),
    (2016, 20738),
    (2016, 20428),
)

class TestGame:
    def __init__(self, season, game):
        self.game = GameContainer(season, game)

    def test(self):
        self.test_teams()
        self.test_hits()
        self.test_faceoffs()
        self.test_goals()
        self.test_shots()
        self.test_turnovers()
        self.test_plays()

    def test_plays(self):
        for play in self.game.scrapi_game.plays:
            if 'team' in play.json:
                assert hasattr(play, 'for_team')
                assert 'id' in play.for_team

                assert hasattr(play, 'against_team')
                assert 'id' in play.against_team

                assert play.for_team['id'] != play.against_team['id']

                json_on_ice = len(play.on_ice['home']) + len(play.on_ice['away'])
                scrapi_on_ice = len(play.home_on_ice) + len(play.vis_on_ice)
                assert json_on_ice == scrapi_on_ice

    def test_teams(self):
        assert hasattr(self.game, 'teams')
        assert isinstance(self.game.teams, dict)

        assert 'away' in self.game.teams
        assert isinstance(self.game.teams['away'], dict)
        assert 'id' in self.game.teams['away']
        assert isinstance(self.game.teams['away']['id'], int)
        assert 'franchise' in self.game.teams['away']
        assert isinstance(self.game.teams['away']['franchise'], dict)
        assert 'franchiseId' in self.game.teams['away']['franchise']
        assert isinstance(self.game.teams['away']['franchise']['franchiseId'], int)

        assert 'home' in self.game.teams
        assert isinstance(self.game.teams['home'], dict)
        assert 'id' in self.game.teams['home']
        assert isinstance(self.game.teams['home']['id'], int)
        assert 'franchise' in self.game.teams['home']
        assert isinstance(self.game.teams['home']['franchise'], dict)
        assert 'franchiseId' in self.game.teams['home']['franchise']
        assert isinstance(self.game.teams['home']['franchise']['franchiseId'], int)

    def test_rosters(self):
        assert hasattr(self.game, 'rosters')
        assert callable(self.game.rosters)

        assert 'home' in self.game.rosters()
        assert 'away' in self.game.rosters()

        for player in self.game.rosters()['home']:
            assert hasattr(player, 'json')
            assert isinstance(player['json'], dict)

            self.test_player(player['json'])

        for player in self.game.rosters()['away']:
            assert hasattr(player, 'json')
            assert isinstance(player['json'], dict)

            self.test_player(player['json'])

    def test_faceoffs(self):
        assert hasattr(self.game, 'faceoffs'), 'No faceoffs method'
        assert callable(self.game.faceoffs), 'No faceoffs method'
        assert iterator_nonempty(self.game.faceoffs()), 'No faceoffs'

        faceoffs_json = self.game.nhl_api.faceoffs_json()
        #assert iterator_nonempty(faceoffs_json), 'No faceoffs from JSON API' # Gotta dump these because some game don't have them

        for faceoff in self.game.faceoffs():
            assert isinstance(faceoff, playbyplay.Play)
            assert isinstance(faceoff.event, events.FaceOff)
            assert hasattr(faceoff, 'time')
            assert isinstance(faceoff.time, dict)

            faceoff_time = faceoff.time
            assert 'min' in faceoff_time
            assert 'sec' in faceoff_time

            assert hasattr(faceoff, 'winner')
            self.test_player(faceoff.winner)

            assert hasattr(faceoff, 'loser')
            self.test_player(faceoff.loser)

            assert hasattr(faceoff, 'for_team')
            assert 'id' in faceoff.for_team

            assert hasattr(faceoff, 'against_team')
            assert 'id' in faceoff.for_team

        first_faceoff = self.game.faceoffs()[0]
        assert first_faceoff.time['min'] == 0
        assert first_faceoff.time['sec'] == 0

    def test_hits(self):
        assert hasattr(self.game, 'hits'), 'No hits method'
        assert callable(self.game.hits), 'No hits method'

        hits = self.game.hits()

        assert len(hits), 'no hits'

        for hit in self.game.hits():
            assert isinstance(hit, playbyplay.Play)
            assert isinstance(hit.event, events.Hit)

            assert hasattr(hit, 'hitter')
            assert self.test_player(hit.hitter)

            assert hasattr(hit, 'hittee')
            assert self.test_player(hit.hittee)

            assert hasattr(hit, 'for_team')
            assert 'id' in hit.for_team

            assert hasattr(hit, 'against_team')
            assert 'id' in hit.against_team

    def test_goals(self):
        assert hasattr(self.game, 'goals'), 'No goals method'
        assert callable(self.game.goals), 'No goals method'

        goals = self.game.goals()

        assert len(goals)

        for goal in goals:
            assert isinstance(goal, playbyplay.Play)
            assert isinstance(goal.event, events.Goal)

            assert hasattr(goal, 'shot_taker')
            assert self.test_player(goal.shot_taker)

            assert hasattr(goal, 'assists')
            assert len(goal.assists) in (0,1,2)

            for assist in goal.assists:
                self.test_player(assist)

            assert hasattr(goal, 'goalie')
            if goal.goalie:
                self.test_player(goal.goalie)

            assert hasattr(goal, 'for_team')
            assert 'id' in goal.for_team

            assert hasattr(goal, 'against_team')
            assert 'id' in goal.against_team

    def test_shots(self):
        assert hasattr(self.game, 'shots'), 'No shots method'
        assert callable(self.game.shots), 'No shots method'

        shots: List[playbyplay.Play] = self.game.shots()

        for miss in shots['misses']:
            assert hasattr(miss, 'shot_taker')
            assert isinstance(miss.shot_taker, dict)
            assert 'id' in miss.shot_taker

            assert hasattr(miss, 'for_team')
            assert 'id' in miss.for_team

            assert hasattr(miss, 'against_team')
            assert 'id' in miss.for_team

        for block in shots['blocks']:
            assert hasattr(block, 'shot_taker')
            assert isinstance(block.shot_taker, dict)
            assert self.test_player(block.shot_taker)

            assert hasattr(block, 'blocker')
            assert isinstance(block.blocker, dict)
            assert self.test_player(block.blocker)

            assert hasattr(block, 'for_team')
            assert 'id' in block.for_team

            assert hasattr(block, 'against_team')
            assert 'id' in block.for_team

        for shot in shots['shots']:
            assert hasattr(shot, 'shot_taker')
            assert isinstance(shot.shot_taker, dict)
            assert self.test_player(shot.shot_taker)

            assert hasattr(shot, 'goalie')
            assert isinstance(shot.goalie, dict)
            assert self.test_player(shot.goalie)

            assert hasattr(shot, 'for_team')
            assert 'id' in shot.for_team

            assert hasattr(shot, 'against_team')
            assert 'id' in shot.for_team

    def test_turnovers(self):
        assert hasattr(self.game, 'turnovers'), 'No turnovers method'
        assert callable(self.game.turnovers), 'No turnovers method'

        turnovers: List[playbyplay.Play] = self.game.turnovers()

        for giveaway in turnovers['giveaways']:
            assert hasattr(giveaway, 'giver')
            assert isinstance(giveaway.giver, dict)
            assert self.test_player(giveaway.giver)

            assert hasattr(giveaway, 'for_team')
            assert 'id' in giveaway.for_team

            assert hasattr(giveaway, 'against_team')
            assert 'id' in giveaway.for_team

        for takeaway in turnovers['takeaways']:
            assert hasattr(takeaway, 'taker')
            assert isinstance(takeaway.taker, dict)
            assert self.test_player(takeaway.taker)

            assert hasattr(takeaway, 'for_team')
            assert 'id' in takeaway.for_team

            assert hasattr(takeaway, 'against_team')
            assert 'id' in takeaway.for_team

    def test_penalties(self):
        assert hasattr(self.game, 'penalties'), 'No penalties method'
        assert callable(self.game.penalties), 'No penalties method'

        penalties = self.game.penalties()

        assert len(penalties)

        for penalty in penalties:
            assert isinstance(penalty, playbyplay.Play)
            assert isinstance(penalty.event, events.penalty)

            assert hasattr(penalty, 'offender')
            assert self.test_player(penalty.offender)

            assert hasattr(penalty, 'drawer')
            assert self.test_player(penalty.drawer)

            assert hasattr(penalty, 'for_team')
            assert 'id' in penalty.for_team

            assert hasattr(penalty, 'against_team')
            assert 'id' in penalty.for_team

    def test_shootout(self):
        assert hasattr(self.game, 'shots'), 'No shots method'
        assert callable(self.game.shots), 'No shots method'

        shots: List[playbyplay.Play] = self.game.shootout()

        for shot in shots:
            print(shot)
            assert hasattr(shot, 'shot_taker')
            assert isinstance(shot.shot_taker, dict)
            assert self.test_player(shot.shot_taker)

            assert hasattr(shot, 'goalie')
            assert isinstance(shot.goalie, dict)
            assert self.test_player(shot.goalie)

            assert hasattr(shot, 'for_team')
            assert 'id' in shot.for_team

            assert hasattr(shot, 'against_team')
            assert 'id' in shot.for_team

        print('shoootout')

    def test_player(self, player):
        assert isinstance(player, dict)

        assert 'id' in player
        assert isinstance(player['id'], int)

        assert 'firstName' in player
        assert isinstance(player['firstName'], str)

        assert 'lastName' in player
        assert isinstance(player['lastName'], str)

        assert 'birthDate' in player
        assert isinstance(player['birthDate'], str) # I'd like to change this

        return True


for game in test_games:
    test = TestGame(game[0], game[1])
    test.test()
