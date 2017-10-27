import requests
API_URL = 'http://www.hotblackrobotics.com/api/1.0/'

class ApiClient(object):
    def __init__(self, token=None):
        self.token = token

    def save(self, data):
        headers = {'Authorization': 'Bearer %s'%self.token}
        body = {
            'data': data
        }
        print(body)
        r = requests.post(API_URL + 'device/data', json=body, headers=headers)
        return r

class UserClient(object):
    def __init__(self, email, password):
        body = {
            'password': password,
            'email': email
            }

        r = requests.post(API_URL + 'login', json=body)
        if r.status_code == 200:
            self.token = r.json()['token']
        else:
            raise AuthenticationError

    def get_data(self, id, page=1, per_page=20):
        headers = {'Authorization': 'Bearer %s'%self.token}
        r = requests.get(API_URL + 'device/{0}?page={1}&per_page={2}'.format(id, page, per_page), headers=headers)
        return r.json()
