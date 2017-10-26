from ahqapiclient.resources import Resource


class Me(Resource):

    def __init__(self, http_client):
        super(Me, self).__init__('/me', http_client)

    def reset_api_key(self):
        return self.put(path=self.rurl('apikey'))

    def set_password(self, password, repeated):
        return self.post(
            path=self.rurl('password'),
            data={
                'password': password,
                'repeated': repeated
            }
        )

    def set_twofactor_secret(self, secret):
        return self.post(
            path=self.rurl('twofactor'),
            data={
                'secret': secret
            }
        )

    def delete_twofactor_secret(self):
        return self.delete(
            path=self.rurl('twofactor')
        )

    def login(self, twofactor=''):
        postdata = None
        if (twofactor != ''):
            postdata = {
                'token': twofactor
            }

        return self.post(
          path=self.rurl('login'),
          data=postdata
        )

    def logout(self):
        return self.post(
            path=self.rurl('logout'),
            data={
            }
        )
