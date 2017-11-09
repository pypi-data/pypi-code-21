from .const import *
from .validator import check_language
from .req import SteamApiRequest


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
        USER_STATS_ENDPOINT,
        '/GetGlobalAchievementPercentagesForApp',
        'v2',
        payload
    )


def get_global_stats_for_game(game_id, count, name, format='json'):
    payload = {
        'gameid': game_id,
        'count': count,
        'name': name,
    }

    return SteamApiRequest.get(
        USER_STATS_ENDPOINT,
        '/GetGlobalStatsForGame',
        'v1',
        payload,
    )


def get_number_of_current_player(app_id):
    """
    Gets the total number of players currently active in the specified app on Steam.

    :param app_id:
    :return:
    """
    payload = {
        'appid': app_id
    }

    return SteamApiRequest.get(
        USER_STATS_ENDPOINT,
        '/GetNumberOfCurrentPlayers',
        'v1',
        payload
    )


@check_language
def get_schema_for_game(key, app_id, language):
    """
    Gets the complete list of stats and achievements for the specified game.

    :param key: web api key
    :param app_id: app id
    :param language: language code
    :return:
    """

    payload = {
        'key': key,
        'appid': app_id,
        'l': language
    }

    return SteamApiRequest.get(
        USER_STATS_ENDPOINT,
        '/GetSchemaForGame',
        'v2',
        payload
    )
