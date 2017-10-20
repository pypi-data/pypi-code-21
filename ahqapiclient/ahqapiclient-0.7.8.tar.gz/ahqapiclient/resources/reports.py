from ahqapiclient.resources import Resource
from six import text_type


class Reports(Resource):

    def __init__(self, http_client):
        super(Reports, self).__init__('/reports', http_client)

    def create_report(self, report_type, value=None, s3_data=None):

        data = {}

        if value:
            if not isinstance(value, text_type):
                value = value.encode('utf-8')
            data['value'] = value

        if s3_data:
            data['s3_data'] = s3_data

        return self.post(
            path=self.rurl(report_type),
            data=data
        )
