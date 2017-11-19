import re
import collections
from itertools import starmap, chain

from nhlscrapi.games.game import Game, GameKey, GameType
from nhlscrapi.games.events import EventType

from nhlscrapi.games.playbyplay import Play

import filters

from nhlapi import NhlApi

from gametime import game_time, period_time

from containers.hits import HitsContainer
from containers.faceoffs import FaceoffsContainer
from containers.goals import GoalsContainer
from containers.shots import ShotsContainer
from containers.turnovers import TurnoversContainer
from containers.penalties import PenaltiesContainer
from containers.shootouts import ShootoutContainer
from containers.shift import ShiftSummary

GAME_TYPES = [None, GameType.PreSeason, GameType.Regular, GameType.Playoffs]
GAME_TYPE_DIVISOR = 10000


# We do a kind of player lookup against the game roster. There's no way to do this
# before 2010. The best way I can think to manage player lookups is to have the user
# of this library provide a function for the lookups, and that would only be used
# in games where the JSON API cannot be used.
class GameContainer():
    def __init__(self, season, game, json={}):
        print(season, game)
        self.season = int(season)
        self.game = int(game)

        self.nhl_api = NhlApi(self.season, self.game, json=json)
        assert isinstance(self.nhl_api, NhlApi)

        self.scrapi_game = self.create_scrapi_game()
        assert isinstance(self.scrapi_game, Game)

        self.teams = self.nhl_api.live_json()['gameData']['teams']
        self.times = self.nhl_api.live_json()['gameData']['datetime']

        self._assign_meta()
        self._assign_on_ice()

        # This is regrettable
        self.faceoffs_container = FaceoffsContainer(self)
        self.faceoffs = self.faceoffs_container.faceoffs # link these methods
        self.faceoffs()

        self.hits_container = HitsContainer(self)
        self.hits = self.hits_container.hits
        self.hits()

        self.goals_container = GoalsContainer(self)
        self.goals = self.goals_container.goals
        self.goals() # Initialize

        self.shots_container = ShotsContainer(self)
        self.shots = self.shots_container.shots
        self.shots() # Initialize

        self.turnovers_container = TurnoversContainer(self)
        self.turnovers = self.turnovers_container.turnovers
        self.turnovers()

        self.penalties_container = PenaltiesContainer(self)
        self.penalties = self.penalties_container.penalties
        self.penalties()

        self.shootout_container = ShootoutContainer(self)
        self.shootout = self.shootout_container.shootout
        self.shootout()

        self.shifts()

        play_types = set()
        for play in self.scrapi_game.plays:
            play_types.add(str(play.event))

    def create_scrapi_game(self):
        game_type = scrapi_game_type(self.game)
        game_number = scrapi_game_number(self.game)
        scrapi_game_key = GameKey(self.season, game_type, game_number)

        return Game(scrapi_game_key, cum_stats={})

    def players(self):
        return self.nhl_api.players_json().values()

    def rosters(self):
        def augment_player(player):
            player.json = self.onice_json_from_scrapi(None, (player['name'],))
            return player

        if not (hasattr(self, '_rosters') and self._rosters):
            self._rosters = {
                'home': list(map(augment_player, self.scrapi_game.rosters.home_skaters)),
                'away': list(map(augment_player, self.scrapi_game.rosters.away_skaters)),
            }

        return self._rosters

    # Doesn't work. 201620047 has issues with Di Giuseppe showing up as GIUSEPPE DI
    def shifts(self):
        if not (hasattr(self, '_shifts') and self._shifts):
            home_shifts = self.scrapi_game.toi.home_shift_summ
            away_shifts = self.scrapi_game.toi.away_shift_summ

            self._shifts = {
                'home': [ShiftSummary(shift_summary, self) for _, shift_summary in home_shifts.items()],
                'away': [ShiftSummary(shift_summary, self) for _, shift_summary in away_shifts.items()],
            }

            # for player_number, shift_summary in chain(home_shifts.items(), away_shifts.items()):
            #     assert hasattr(shift_summary, 'player_name')
            #     assert 'first' in shift_summary.player_name
            #     assert 'last' in shift_summary.player_name
            #
            #     player_name = shift_summary.player_name['first'] + ' ' + shift_summary.player_name['last']
            #     shift_summary.player = self.onice_json_from_scrapi(player_number, [player_name])
            #
            #     for shift in shift_summary.shifts:
            #         shift['state'] = self._find_state(shift['period'], period_time(shift['end']))
            #
            # self._shifts = list(home_shifts.items()) + list(away_shifts.items())

        return self._shifts

    def _transform_play(self, play):
        assert isinstance(play, Play)
        assert hasattr(play, 'home_on_ice')
        assert isinstance(play.home_on_ice, dict)

        assert hasattr(play, 'vis_on_ice')
        assert isinstance(play.vis_on_ice, dict)

        play.on_ice = {
            'home': list(starmap(self.onice_json_from_scrapi, play.home_on_ice.items())),
            'away': list(starmap(self.onice_json_from_scrapi, list(play.vis_on_ice.items()))),
            #'bucket': calculate_bucket(play)
        }

        for num, info in zip(list(play.vis_on_ice.keys()), list(play.vis_on_ice.values())):
            player = self.onice_json_from_scrapi(num, info)
            play.on_ice['away'].append(player)

        if 'team' in play.json:
            play.for_team = self.teams['home'] if self.teams['home']['id'] == play.json['team']['id'] else self.teams['away']
            play.against_team = self.teams['away'] if self.teams['home']['id'] == play.json['team']['id'] else self.teams['home']

        return play

    def onice_json_from_scrapi(self, number, info):
        assert len(info)
        assert isinstance(info[0], str)

        games_players = list(self.players())

        if len(info) > 2:
            player_name = '-'.join(reversed(info[:-1]))
        else:
            player_name = info[0]

        info_first_name, info_last_name = name_string_split(player_name)

        for game_player in games_players:
            name_match = game_player['fullName'].upper() == player_name.upper()
            silly_match_attempt = game_player['firstName'].upper() in player_name and game_player['lastName'].upper() in player_name

            # reverse of the silly match
            silly_match_reverse = info_first_name in game_player['fullName'].upper() and info_last_name in game_player['fullName'].upper()

            if name_match or silly_match_attempt or silly_match_reverse:
                match = game_player
                break

        else:
            # absolute last case scenario - we really don't want to get here
            # collect all with last name
            last_name_matches = list(filter(lambda p: p['lastName'].upper() == info_last_name, games_players))
            best_match = None
            matches = -1
            for last_name_match in last_name_matches:
                overlap = len([i for i,j in zip(last_name_match['lastName'], info_last_name) if i.upper() == j.upper()])
                if overlap > matches:
                    best_match = last_name_match

            match = best_match

        if len(info) >= 2 and match:
            match['position'] = info[-1]

        return match

    def play_types_match(self, play, play_json):
        json_play_type = re.sub('\s+', '', play_json['result']['event'].lower())
        scrapi_play_type = str(play.event).lower()

        return json_play_type.startswith(scrapi_play_type)

    def _assign_meta(self):
        all_plays = self.scrapi_game.plays

        json_events = list(self.nhl_api.pbp_json()[1:])
        json_plays = filter(is_period_start, json_events)

        for play in all_plays:
            for play_json in json_events:
                if game_time(play_json['about']['period'], play_json['about']['periodTime']) == game_time(play.period, play.time) and self.play_types_match(play, play_json):
                    play.coordinates = play_json['coordinates']
                    play.id = int(play_json['about']['eventId'])

                    play.json = play_json
                    play.type = play_json['result']['event'].lower()
                    break

            else:
                play.json = {}
                play.type = str(play.event).lower()

    def _assign_on_ice(self):
        all_plays = self.scrapi_game.plays
        for play in all_plays:
            play.on_ice = self.scrapi_onice_to_json(play)

            if 'team' in play.json:
                play.for_team = self.teams['home'] if self.teams['home']['id'] == play.json['team']['id'] else \
                self.teams['away']
                play.against_team = self.teams['away'] if self.teams['home']['id'] == play.json['team']['id'] else \
                self.teams['home']

    def scrapi_onice_to_json(self, play):
        home_scrapi_onice = play.home_on_ice
        away_scrapi_onice = play.vis_on_ice
        return {
            'home': [o for o in [self.onice_json_from_scrapi(num, info) for num, info in home_scrapi_onice.items()] if o],
            'away': [o for o in [self.onice_json_from_scrapi(num, info) for num, info in away_scrapi_onice.items()] if o],
        }

    def _find_state(self, period, time):
        for play in reversed(self.scrapi_game.plays):
            if play.period == period and period_time(play.time) < time:
                return play.state

    def event_players_from_type(self, event_players, player_type):
        # In the interest of speed, player_type_match returns a curried function that
        # checks if the types are the same.
        # You know what I had before? I had this:
        # return [player['player'] for player in event_players if player['playerType'].lower() == player_type][0]
        # But I've heard that's not as fast, and I believe it.
        # I don't find this any less readable.
        #   1. Filter the players by type, which returns an iterator
        #   2. Grab the first one
        #   3. Grab the 'player' value from it

        matches = list(filter(filters.player_type_match(player_type), event_players))
        return [match['player'] for match in matches]

    def event_participants(self, event, participant_types):
        assert isinstance(participant_types, collections.Iterable)
        assert isinstance(event, Play)

        event_json = event.json

        participants = {}
        for participant_type in participant_types:
            if event_json:
                participant_matches = self.event_players_from_type(event_json['players'], participant_type)
                participants[participant_type] = participant_matches
            elif hasattr(event.event, 'participants'):
                participant_matches = self.get_participant_old(event, participant_type)
                participants[participant_type] = participant_matches

        return participants


    def get_participant_old(self, play, participant_type: str, basic=False) -> dict:
        participants: list = []

        if participant_type == 'goalie':
            other_participant: str = (self.get_participant_old(play, 'shooter', True) or self.get_participant_old(play, 'scorer', True))[0][1]
            if play.event.home_abbr in other_participant['team']:
                on_ices = play.on_ice['away']
            else:
                on_ices = play.on_ice['home']

            for on_ice in on_ices:
                if on_ice['position'].startswith('G'):
                    participants.append(on_ice)

        else:
            for participant in play.event.participants:
                participant_name: str = participant['name'].upper()

                if participant['playerType'].lower() == participant_type.lower():
                    on_ice_roster = []
                    other_roster = []
                    if participant['num'] in play.home_on_ice: on_ice_roster += play.on_ice['home']
                    if participant['num'] in play.vis_on_ice: on_ice_roster += play.on_ice['away']

                    added_at_least_one = False
                    for on_ice in on_ice_roster:
                        on_ice_name: str = on_ice['lastName'].upper()

                        if on_ice_name == participant_name:
                            if not basic:
                                participants.append(on_ice)
                            else:
                                participants.append((on_ice, participant))

                            added_at_least_one = True

                    if not added_at_least_one:
                        for player in self.players():
                            if player['lastName'].upper() == participant_name:
                                if not basic:
                                    participants.append(player)
                                else:
                                    participants.append((player, participant))
                                break

        return participants


def scrapi_game_type(game):
    game_number_int = int(game) # could be a string
    game_type_digit = game_number_int // GAME_TYPE_DIVISOR

    return GAME_TYPES[game_type_digit]

def scrapi_game_number(game):
    game_number_int = int(game) # could be a string
    game_number = game_number_int % GAME_TYPE_DIVISOR

    return game_number

def is_period_start(play):
    assert 'result' in play
    assert 'event' in play['result']

    play_type = play['result']['event'].lower()

    is_period_play = 'period' in play_type
    is_period_start = 'period start' in play_type
    is_period_end = 'period end' in play_type

    return (not is_period_play) or is_period_start or is_period_end

def name_string_split(name):
    first_name, *rest = name.split()
    last_name = ' '.join(rest)

    return first_name, last_name
