from .const import *
from .req import SteamApiRequest


# ISteamUser
def get_friend_list(key, steam_id, relationship):
    """
    Returns the friend list of any Steam user, provided their Steam Community profile visibility is set to "Public".

    :param key:
    :param steam_id: 64 bit Steam ID to return friend list for.
    :param relationship: Relationship filter. Possibles values: all, friend.
    :return:
    """

    payload = {
        'key': key,
        'steamid': steam_id,
        'relationship': relationship,
    }

    return SteamApiRequest.get(
        USER_ENDPOINT, '/GetFriendList', 'v1',
        payload
    )


def get_player_bans(key, steam_ids):
    """
    GetPlayerBans returns Community, VAC, and Economy ban statuses for given players.

    :param key:
    :param steam_ids: Comma-delimited list of SteamIDs
    :return:
    """

    payload = {
        'key': key,
        'steamids': steam_ids,
    }

    return SteamApiRequest.get(
        USER_ENDPOINT,
        '/GetPlayerBans',
        'v1',
        payload
    )


def get_player_summaries(key, steam_ids):
    """
    Returns basic profile information for a list of 64-bit Steam IDs.

    :param key: Web API token
    :param steam_ids: Comma-delimited list of 64 bit Steam IDs to return profile information for.
      Up to 100 Steam IDs can be requested.
    :return:
    """

    payload = {
        'key': key,
        'steamids': steam_ids
    }

    return SteamApiRequest.get(
        USER_ENDPOINT, '/GetPlayerSummaries', 'v2',
        payload
    )


def get_user_group_list(key, steam_id):
    """
    list of SteamGroup
    :param key:
    :param steam_id:
    :return:
    """

    payload = {
        'key': key,
        'steamid': steam_id,
    }

    return SteamApiRequest.get(
        USER_ENDPOINT,
        '/GetUserGroupList',
        'v1',
        payload
    )


def resolve_vanity_url(key, vanityurl, url_type):
    """
    Currently ResolveVanityURL gives you a users steamID and that's it.
    It would be nice when you call ResolveVanityURL it gives you the entire users profile like GetPlayerSummaries does.
    Currently you have to make two calls just to get a players name if they are using a vanityURL
    :param key:
    :param vanityurl: The vanity URL to get a SteamID for
    :param url_type:  The type of vanity URL. 1 (default): Individual profile, 2: Group, 3: Official
    :return:
        steamid (Optional)
            The 64 bit Steam ID the vanity URL resolves to. Not returned on resolution failures
    """

    payload = {
        'key': key,
        'vanityurl': vanityurl,
        'url_type': url_type
    }

    return SteamApiRequest.get(
        USER_ENDPOINT,
        '/ResolveVanityURL',
        'v0001',
        payload
    )


# ISteamUserStats
def get_player_achievements(key, steam_id, app_id, language):
    """
    Returns a list of achievements for this user by app id

    :param key:
    :param steam_id: 64 bit Steam ID to return friend list for.
    :param app_id: The ID for the game you're requesting
    :param language: Language. If specified, it will return language data for the requested language.
    :return: A list of achievements.
    """

    payload = {
        'key': key,
        'steamid': steam_id,
        'appid': app_id,
        'l': language,
    }

    return SteamApiRequest.get(
        USER_STATS_ENDPOINT,
        '/GetPlayerAchievements/',
        'v0001',
        payload
    )


def get_user_stats_for_game(key, steam_id, app_id, language):
    """
    Returns a list of achievements for this user by app id

    :param key:
    :param steam_id:
    :param app_id:
    :param language:
    :return:
    """

    payload = {
        'key': key,
        'steamid': steam_id,
        'appid': app_id,
        'l': language,
    }

    return SteamApiRequest.get(
        USER_STATS_ENDPOINT,
        '/GetUserStatsForGame',
        'v0002',
        payload
    )


# IPlayerService
def get_recently_played_games(key, steam_id, count):
    """
    Gets information about a player's recently played games
    :param key:
    :param steam_id:
    :param count:
    :return:
    """
    payload = {
        'key': key,
        'steamid': steam_id,
        'count': count
    }

    return SteamApiRequest.get(
        PlAYER_ENDPOINT,
        '/GetRecentlyPlayedGames',
        'v0001',
        payload
    )


def get_owned_game(key, steam_id, include_appinfo,
                   include_played_free_games, appids_filter):
    """
    GetOwnedGames returns a list of games a player owns along with some playtime information,
    if the profile is publicly visible. Private, friends-only, and other privacy settings are not supported unless
    you are asking for your own personal details (ie the WebAPI key you are using is linked to the steamid you are
    requesting).

    :param key:
    :param steam_id: The SteamID of the account.
    :param include_appinfo: Include game name and logo information in the output. The default is to return appids only.
    :param include_played_free_games:
    :param appids_filter: Note that these cannot be passed as a URL parameter
    :return:
    """
    payload = {
        'key': key,
        'steamid': steam_id,
        'include_appinfo': include_appinfo,
        'include_played_free_games': include_played_free_games,
        'appids_filter': appids_filter,
    }

    return SteamApiRequest.get(
        PlAYER_ENDPOINT,
        '/GetOwnedGames',
        'v0001',
        payload
    )


def get_steam_level(key, steam_id):
    """
    Returns the Steam Level of a user
    :param key:
    :param steam_id:
    :return:
    """

    payload = {
        'key': key,
        'steamid': steam_id,
    }

    return SteamApiRequest.get(
        PlAYER_ENDPOINT,
        '/GetSteamLevel',
        'v1',
        payload
    )


def get_badges(key, steam_id):
    """
    "Gets badges that are owned by a specific user"
    :param key:
    :param steam_id:
    :return:
    """

    payload = {
        'key': key,
        'steamid': steam_id,
    }

    return SteamApiRequest.get(
        PlAYER_ENDPOINT,
        '/GetBadges',
        'v1',
        payload
    )


def get_community_badge_progress(key, steam_id, badge_id):
    """

    :param key:
    :param steam_id:
    :param badge_id:
    :return:
    """

    payload = {
        'key': key,
        'steamid': steam_id,
        'badgeid': badge_id,
    }

    return SteamApiRequest.get(
        PlAYER_ENDPOINT,
        '/GetCommunityBadgeProgress',
        'v1',
        payload
    )


def is_playing_shared_games(key, steam_id, app_id):
    """
    IsPlayingSharedGame returns the original owner's SteamID if a borrowing account is currently playing this game.
     If the game is not borrowed or the borrower currently doesn't play this game, the result is always 0.

    :param key:
    :param steam_id:
    :param app_id:
    :return:
    """

    payload = {
        'key': key,
        'steamid': steam_id,
        'appid_playing': app_id
    }

    return SteamApiRequest.get(
        PlAYER_ENDPOINT,
        '/IsPlayingSharedGame',
        'v1',
        payload
    )
