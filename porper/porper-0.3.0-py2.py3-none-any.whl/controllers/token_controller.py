
from datetime import datetime

class TokenController:

    def __init__(self, connection):
        self.connection = connection
        from porper.models.access_token import AccessToken
        self.access_token = AccessToken(connection)

    def find_user_id(self, access_token):
        params = {
            'access_token': access_token
        }
        return self.find(params)[0]['user_id']

    def create(self, access_token, params):
        return self.save(params['access_token'], params['refresh_token'], params['user_id'])

    def save(self, access_token, refresh_token, user_id):
        params = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'refreshed_time': str(datetime.utcnow())
        }
        if user_id: params['user_id'] = user_id
        rows = self.access_token.find(params)
        if len(rows) == 0:
            print 'saving tokens : %s' % params
            return self.access_token.create(params)
        else:
            print 'updating token : %s' % params
            return self.access_token.update(params)

    def find(self, params):
        rows = self.access_token.find(params)
        if len(rows) == 0:
            raise Exception("unauthorized")
        return rows
