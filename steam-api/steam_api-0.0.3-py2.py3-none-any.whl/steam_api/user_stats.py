from .api import SteamApiRequest, USER_STATS_ENDPOINT


# API call
def get_global_achievements_for_app(game_id, format='json'):
    """
    Returns on global achievements overview of a specific game in percentages.

    :param game_id:
    :param format:
    :return:
    """

    payload = {
        'gameid': game_id,
        'format': format,
    }

    return SteamApiRequest.get(
        USER_STATS_ENDPOINT, '/GetGlobalAchievementPercentagesForApp', 'v0002',
        payload
    )


def get_global_stats_for_game(game_id, count, name, format='json'):
    # ISteamUserStats /GetGlobalStatsForGame / v0001 /?
    # format = xml & appid = 17740 & count = 1 &name[0]global.map.emp_isle
    # {
    #     response: {
    #         globalstats: {
    # global.map.emp_isle: {
    #     total: "26308385566"
    # }
    # },
    # result: 1
    # }
    # }
    pass


class GameUserStats(object):
    def __init__(self, game_id):
        if game_id is None:
            raise ValueError('game id can not be empty')

        self.game_id = game_id

    @property
    def achievements(self):
        try:
            res = get_global_achievements_for_app(self.game_id)
            achievements = res['achievementpercentages']

            return achievements['achievements']

        except ValueError:
            return []
