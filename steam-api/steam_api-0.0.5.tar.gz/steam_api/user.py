from .api.user import *
from future.utils import python_2_unicode_compatible
from .error import ParameterNotInEnumError, ParameterRequiredError


@python_2_unicode_compatible
class User(object):
    """
    User Service
    """

    def __init__(self, key=None, steam_id=None):
        """
        init user class

        :param key: web api key
        :param steam_id: steam id
        :raises ParameterRequiredError: if `steam_id` or `key` is not provided
        """

        #: api key
        if key is None:
            raise ParameterRequiredError('key can not be empty')

        if steam_id is None:
            raise ParameterRequiredError('steam_id can not be empty')

        self.key = key
        self.steam_id = steam_id

    def __str__(self):
        return '<Steam User with id: {id}>'.format(id=self.steam_id)

    @property
    def profile(self):
        """
        user's profile

        :return: {personaname: ''}
        """

        res = get_player_summaries(self.key, self.steam_id)
        profile = res['response']
        return profile['players'][0]

    def profiles(self, steam_id_list=None):
        """
        multi users profile

        :param steam_id_list: list of steam ids, e.g. [1, 2, 3]
        :return: [{personaname: ''}]
        """
        if type(steam_id_list) is 'list':
            user_id = ','.join(steam_id_list)
        else:
            user_id = self.steam_id

        res = get_player_summaries(self.key, user_id)
        profiles = res['response']
        return profiles['players']

    def friends(self, relationship='all'):
        """
        get friends list

        :param relationship: Enum, `all` or `friend`
        :return:
        """
        res = get_friend_list(self.key, self.steam_id, relationship)
        friends = res['friendslist']
        return friends['friends']

    def game_achievements(self, app_id=None, language=''):
        """
        get user's achievements of this game

        :param app_id:
        :param language:
        :return:
        """

        res = get_player_achievements(self.key, self.steam_id, app_id, language)
        return res['playerstats']

    def game_stats(self, app_id=None, language=''):
        """
        get user's stats of this game

        :param app_id:
        :param language:
        :return:
        """
        res = get_user_stats_for_game(self.key, self.steam_id, app_id, language)
        return res['playerstats']

    def owned_games(self, include_appinfo=True,
                    include_played_free_games=True, appids_filter=[]):
        """
        get owned game list

        :param include_appinfo:
        :param include_played_free_games:
        :param appids_filter:
        :return:
        """

        res = get_owned_game(self.key, self.steam_id,
                             include_appinfo, include_played_free_games, appids_filter)
        return res['response']

    def recently_played_games(self, limit=1):
        """
        get recently played games list

        :param limit:
        :return:
        """

        res = get_recently_played_games(self.key, self.steam_id, limit)
        return res['response']

    @property
    def badges(self):
        """
        get badges

        :return:
        """

        res = get_badges(self.key, self.steam_id)
        return res['response']

    @property
    def steam_level(self):
        """
        get steam level

        :return:
        """

        res = get_steam_level(self.key, self.steam_id)
        return res['response']

    @property
    def groups(self):
        """
        get groups

        :return:
        """

        res = get_user_group_list(self.key, self.steam_id)
        return res['response']

    @property
    def is_playing_shared_game(self):
        """
        is playing shared game or not

        :return:
        """
        pass

    @property
    def bans(self):
        # TODO
        # handle multi users input
        """
        get banned list

        :return:
        """

        res = get_player_bans(self.key, self.steam_id)
        return res['response']

