import requests

STEAM_API_URL = 'http://api.steampowered.com'
NEWS_ENDPOINT = '/ISteamNews'
USER_STATS_ENDPOINT = '/ISteamUserStats'
USER_ENDPOINT = '/ISteamUser'
PlAYER_ENDPOINT = '/IPlayerService'


class SteamApiRequest:
    def __init__(self):
        pass

    @staticmethod
    def get(endpoint, path, version, payload):
        url = '{domain}{endpoint}{path}/{version}'.format(
            domain=STEAM_API_URL,
            endpoint=endpoint,
            path=path,
            version=version,
        )

        r = requests.get(url, params=payload)
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            raise ValueError(r.json())

    def post(self):
        pass

