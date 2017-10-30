from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationBase(object):
    _message = 'Hello, World'
    _extra = None
    _badge = None
    _content_available = None
    _thread_id = None

    @property
    def message(self):
        return self._message

    @property
    def additional_data(self):
        data = {
            'extra': self._extra,
            'badge': self._badge,
            'content_available': self._content_available,
            'thread_id': self._thread_id
        }

        return {key: value for key, value in data.items() if value is not None}

    def __str__(self):
        return str({'message': self.message, 'additional_data': self.additional_data})


class FormattedNotification(NotificationBase):
    _data = ()

    @property
    def data(self):
        return self._data

    @property
    def message(self):
        assert isinstance(self.data, tuple)
        return self._message % self.data
