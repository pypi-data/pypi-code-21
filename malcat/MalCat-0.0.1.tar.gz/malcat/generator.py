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


class MalCat(object):
    """Quick-use API"""

    def __init__(self, status_headers=DEFAULT_STATUS_HEADERS):
        self._status_headers = status_headers
        self._series_formatters = {
            media_type: SeriesFormatter(media_type)
            for media_type in MediaType
        }
        self._status_formatters = {
            media_type: StatusFormatter(self._status_headers[media_type])
            for media_type in MediaType
        }
        self._myanimelist = Myanimelist()

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
