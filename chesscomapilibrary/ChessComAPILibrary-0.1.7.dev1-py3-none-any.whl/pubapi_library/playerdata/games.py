"""TODO: docstring"""
from tortilla import wrap

from pubapi_library.settings import REQUEST_HEADERS
from .profile import Player


class DailyGames:
    def __init__(self, player_username):
        self.player = Player(player_username)

    def current_daily_games(self):
        """Returns a list of current daily games by player."""
        return wrap(self.player.id()
                    ).games.get(headers=REQUEST_HEADERS)['games']

    def to_move_daily_games(self):
        """Returns a list of games where it is the players turn to move."""
        return wrap(self.player.id()
                    ).games('to-move').get(headers=REQUEST_HEADERS)['games']


class MonthlyArchives:
    def __init__(self, player_username, archive_year, archive_month,
                 opponent_username=None):
        self.player = Player(player_username)
        self.opponent = (None
                         if opponent_username is None
                         else Player(opponent_username))
        self.year = archive_year
        self.month = archive_month

    def games_in_archive(self):
        """Returns list of games in a players monthly archive."""
        return wrap(self.player.id()).games(f'{self.year}/{self.month:02d}'
                                            ).get(headers=REQUEST_HEADERS
                                                  )['games']

    def list_of_games_played_against(self):
        """List of games the player has played against an opponent."""
        return [game for game in self.games_in_archive()
                if
                game['white']['@id'] == self.opponent.id() or
                game['black']['@id'] == self.opponent.id()]

    def games_played_against_opponent_of_a_certain_colour(self, opponent_colour
                                                          ):
        """List of game/s against an opponent who was a certain colour.

        Args:
            opponent_colour str: `white` or `black`
        """
        return [game for game in self.games_in_archive()
                if game[opponent_colour.lower()]['@id'] == self.opponent.id()]
