from datetime import datetime

from ahqapiclient.resources import Resource


DT_FORMAT = r'%Y-%m-%dT%H:%M:%SZ'


class Log(Resource):

    def __init__(self, http_client):
        super(Log, self).__init__('/logs', http_client)

    def make_doc(self, date, facility, level, message, tags=None):
        if tags is None:
            tags = []

        if isinstance(date, datetime):
            date = date.strftime(DT_FORMAT)

        return {
            'date': date,
            'facility': facility,
            'level': level,
            'message': message,
            'tags': tags,
        }

    def create_log(self, date, facility, level, message, tags=None):
        return self.post(
            path=self.rurl(),
            data=self.make_doc(date, facility, level, message, tags)
        )

    def get_log(self, _id):
        return self.get(path=self.rurl(_id))

    def get_logs(self, date_from=None, date_to=None, limit=10, offset=0,
                 query='', sort='date:desc'):
        if isinstance(date_from, datetime):
            date_from = date_from.strftime(DT_FORMAT)

        if isinstance(date_to, datetime):
            date_to = date_to.strftime(DT_FORMAT)

        return self.get(
            path=self.rurl(),
            params={
                'date_from': date_from,
                'date_to': date_to,
                'limit': limit,
                'offset': offset,
                'query': query,
                'sort': sort,
            }
        )

    def get_summary(self, date_from, date_to, limit=10, offset=0, query='',
                    sort='date:desc'):
        if isinstance(date_from, datetime):
            date_from = date_from.strftime(DT_FORMAT)

        if isinstance(date_to, datetime):
            date_to = date_to.strftime(DT_FORMAT)

        return self.get(
            path=self.rurl('summary'),
            params={
                'date_from': date_from,
                'date_to': date_to,
                'limit': limit,
                'offset': offset,
                'query': query,
                'sort': sort,
            }
        )

    def log_system_info(self, message, date=None, tags=None):
        if date is None:
            date = datetime.utcnow()

        return self.create_log(
            date=date,
            facility='system',
            level='info',
            message=message,
            tags=tags
        )

    def log_system_warning(self, message, date=None, tags=None):
        if date is None:
            date = datetime.utcnow()

        return self.create_log(
            date=date,
            facility='system',
            level='warning',
            message=message,
            tags=tags
        )

    def log_system_error(self, message, date=None, tags=None):
        if date is None:
            date = datetime.utcnow()

        return self.create_log(
            date=date,
            facility='system',
            level='error',
            message=message,
            tags=tags
        )
