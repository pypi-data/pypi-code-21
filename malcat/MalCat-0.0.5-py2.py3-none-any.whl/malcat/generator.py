from myanimelist.api import Myanimelist
from myanimelist.models import MediaStatus, MediaType, User

from malcat.series import SeriesFormatter
from malcat.status import StatusFormatter


DEFAULT_STATUS_HEADERS = {
    MediaType.ANIME: {
        MediaStatus.CURRENT: 'Watching',
        MediaStatus.COMPLETED: 'Completed',
        MediaStatus.ON_HOLD: 'On Hold',
        MediaStatus.DROPPED: 'Dropped',
        MediaStatus.PLANNED: 'Plan to Watch'
    },
    MediaType.MANGA: {
        MediaStatus.CURRENT: 'Reading',
        MediaStatus.COMPLETED: 'Completed',
        MediaStatus.ON_HOLD: 'On Hold',
        MediaStatus.DROPPED: 'Dropped',
        MediaStatus.PLANNED: 'Plan to Read'
    }
}


class _CachedMyanimelist(Myanimelist):

    def __init__(self, cache):
        Myanimelist.__init__(self)
        self._cache = cache

    def user_media(self, user, media_type):
        cache_key = '{}-{}-media'.format(user.name, media_type.value).lower()
        media = self._cache.get(cache_key)
        if media is None:
            media = Myanimelist.user_media(self, user, media_type)
            self._cache.set(cache_key, media)
        return media

    def user_profile(self, user):
        cache_key = '{}-profile'.format(user.name).lower()
        profile = self._cache.get(cache_key)
        if profile is None:
            profile = Myanimelist.user_profile(self, user)
            self._cache.set(cache_key, profile)
        return profile


class MalCat(object):
    """Quick-use API"""

    def __init__(self, cache=None, status_headers=DEFAULT_STATUS_HEADERS):
        self._status_headers = status_headers
        self._series_formatters = {
            media_type: SeriesFormatter(media_type)
            for media_type in MediaType
        }
        self._status_formatters = {
            media_type: StatusFormatter(self._status_headers[media_type])
            for media_type in MediaType
        }
        self._myanimelist = _CachedMyanimelist(cache) if cache is not None else Myanimelist()

    def media(self, user_name, media_type_name, template):
        user = User(user_name)
        media_type = MediaType(media_type_name)

        media = self._myanimelist.user_media(user, media_type)
        text = self._series_formatters[media_type].format_media(media, template)
        return text

    def statuses(self, user_name, media_type_name, template):
        user = User(user_name)
        media_type = MediaType(media_type_name)

        profile = self._myanimelist.user_profile(user)
        statuses = profile.statistics.media_status_breakdown[media_type]
        text = self._status_formatters[media_type].format_statuses(statuses, template)
        return text
