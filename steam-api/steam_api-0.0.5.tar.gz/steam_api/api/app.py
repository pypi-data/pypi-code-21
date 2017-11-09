from .req import SteamApiRequest
from .const import APP_ENDPOINT


def get_app_list():
    return SteamApiRequest.get(
        APP_ENDPOINT,
        '/GetAppList',
        'v2',
    )
