import base64
import string
import requests
from collections import OrderedDict
from tpcli.teampass.exceptions import TeampassHttpException, TeampassApiException
from treelib import Tree
from tabulate import tabulate
from pwgen import pwgen


class TeampassClient:
    TYPE_MODIFICATION = {'item': 'items', 'folder': 'folders'}

    def __init__(self, api_endpoint, api_key):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        requests.packages.urllib3.disable_warnings()

    def list(self, type):
        if type in self.TYPE_MODIFICATION:
            local_type = self.TYPE_MODIFICATION[type]

        url = '{0}/list/{1}?apikey={2}'\
              .format(self.api_endpoint, local_type, self.api_key)
        req = requests.get(url, verify=False)
        if req.status_code != 200:
            raise TeampassHttpException(req.status_code, req.json()['err'])
        else:
            result = self.__format_result(type, req.json())
            return result

    def get(self, type, id):
        url = '{0}/get/{1}/{2}?apikey={3}'\
              .format(self.api_endpoint, type, id, self.api_key)
        req = requests.get(url, verify=False)

        if req.status_code != 200:
            if req.json() and 'err' in req.json():
                raise TeampassApiException(req.json()['err'])
            else:
                raise TeampassHttpException(req.status_code, req.text)
        else:
            if 'err' in req.json() and req.json()['err'] == 'No results':
                raise TeampassApiException(req.json()['err'])
            else:
                result = self.__format_result(type, req.json())
                return result

    def search(self, type, search_string):
        if type in self.TYPE_MODIFICATION:
            local_type = self.TYPE_MODIFICATION[type]

        url = '{0}/find/{1}/{2}?apikey={3}'\
              .format(self.api_endpoint, local_type, search_string, self.api_key)
        req = requests.get(url, verify=False)
        if req.status_code != 200:
            if req.json() and 'err' in req.json():
                raise TeampassApiException(req.json()['err'])
            else:
                raise TeampassHttpException(req.status_code, req.text)
        else:
            if 'err' in req.json() and req.json()['err'] == 'No results':
                raise TeampassApiException(req.json()['err'])
            else:
                result = self.__format_result(type, req.json())
                return result

    def add(self, type, label, login, pwd, description, folder):
        if type == 'item':
            if description:
                description = description.replace('\\r\\n', '<br />')

            if not pwd:
                pwd = pwgen(16, symbols=False, no_ambiguous=True)

            payload_data = ['' if item is None else item for item in [label, pwd, description, folder, login, '', '', '', '1']]
            payload = base64.b64encode(string.join(payload_data, ';'))

        elif type == 'folder':
            payload = base64.b64encode(string.join([label, '0', folder, '0', '0'], ';'))

        url = '{0}/add/{2}/{3}?apikey={1}'\
              .format(self.api_endpoint,
                      self.api_key,
                      type,
                      payload)

        req = requests.get(url, verify=False)
        if req.status_code != 200:
            if req.json() and 'err' in req.json():
                raise TeampassApiException(req.json()['err'])
            else:
                raise TeampassHttpException(req.status_code, req.text)
        else:
            if 'new_item_id' in req.json():
                return self.get(type, req.json()['new_item_id'])
            elif 'new_folder_id' in req.json():
                return self.get(type, req.json()['new_folder_id'])
            elif 'err' in req.json():
                raise TeampassApiException(req.json()['err'])

    def delete(self, type, id):
        url = '{0}/delete/{1}/{2}?apikey={3}'\
              .format(self.api_endpoint, type, id, self.api_key)
        req = requests.get(url, verify=False)

        if req.status_code != 200:
            if req.json() and 'err' in req.json():
                raise TeampassApiException(req.json()['err'])
            else:
                raise TeampassHttpException(req.status_code, req.text)
        else:
            if 'err' in req.json():
                raise TeampassApiException(req.json()['err'])

            elif 'status' in req.json():
                return req.json()['status']

    def edit(self, type, id, label, login, pwd, description, folder):
        if type == 'item':
            if description:
                description = description.replace('\\r\\n', '<br />')
            payload_data = ['' if item is None else item for item in [label, pwd, description, folder, login, '', '', '', '1']]
            payload = base64.b64encode(string.join(payload_data, ';'))
            url = '{0}/update/{1}/{2}/{3}?apikey={4}'\
                  .format(self.api_endpoint, type, id, payload, self.api_key)
        req = requests.get(url, verify=False)

        if req.status_code != 200:
            if req.json() and 'err' in req.json():
                raise TeampassApiException(req.json()['err'])
            else:
                raise TeampassHttpException(req.status_code, req.text)
        else:
            if 'err' in req.json():
                raise TeampassApiException(req.json()['err'])

            elif 'status' in req.json():
                return self.get(type, id)

    def __format_result(self, type, data):
        result = []
        for item in data:
            if type == 'folder':
                result.append(OrderedDict([
                                          ('ID', item['id']),
                                          ('Parent_ID', item['parent_id']),
                                          ('Title', item['title']),
                                          ('Path', item['path'])
                                          ]))
            elif type == 'item':
                result.append(OrderedDict([
                                          ('ID', item['id']),
                                          ('Label', item['label']),
                                          ('Login', item['login']),
                                          ('Password', item['pw']),
                                          ('Description', item['description'].replace('&nbsp;', ' ').replace('<br />', '\r\n             ')),
                                          ('Path', '{} (ID: {})'.format(item['path'], item['folder_id']))
                                          ]))
        return result

    def print_result_list(self, type, data):
        for item in data:
            if type == 'folder':
                print('ID:    {}'.format(item['ID']))
                print(u'Title: {}'.format(item['Title']))
                print(u'Path:  {}'.format(item['Path']))

            elif type == 'item':
                print('ID:          {}'.format(item['ID']))
                print(u'Label:       {}'.format(item['Label']))
                print(u'Login:       {}'.format(item['Login']))
                print(u'Password:    {}'.format(item['Password']))
                print(u'Description: {}'.format(item['Description']))
                print(u'Path:        {}'.format(item['Path']))
            print('')

    def print_result_table(self, data):
        return tabulate(data, headers='keys', tablefmt='psql')

    def print_result_tree(self, data):
        tree = Tree()
        tree.create_node('', '0')

        for item in data:
            tree.create_node(u'{} ({})'.format(item['Title'], item['ID']), item['ID'], parent=item['Parent_ID'])
        return tree.show()
