import json
import requests

# Version: 0.1
BASE_URL = 'https://easyapi.io/api/v1'

class Object:
    def __init__(self, apiKey, appId):
        self.apiKey = apiKey
        self.appId = appId

    # Create
    # args:
    # 1. data
    # 2. isPublic
    # 3. type
    # 4. replaceId
    # 5. path
    def create(self, *args):
        if (len(args) == 0):
            return { 'success': False, 'message': 'Error: Invalid parameters' }
        data = args[0]

        isPublic = False
        if (len(args) >= 2):
            isPublic = args[1]

        typeStr = ''
        if (len(args) >= 3):
            typeStr = args[2]

        path = ''
        if (len(args) >= 4):
            path = args[3]

        replaceId = ''
        if (len(args) >= 5):
            replaceId = args[4]


        post_fields = {
            'apiKey': self.apiKey,
            'app': self.appId,
            'object': json.dumps(data),
            'isPublic': isPublic,
            'type': typeStr,
            'replaceId': replaceId,
            'path': path
        }
        result = requests.post((BASE_URL + '/objects/create'), post_fields)
        print (result)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # Delete
    def delete(self, objectId):
        post_fields = { 'apiKey': self.apiKey, 'app': self.appId, 'objectId': objectId }
        result = requests.post((BASE_URL + '/objects/delete'), post_fields)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # Get
    def get(self, objectId):
        post_fields = { 'apiKey': self.apiKey, 'app': self.appId, 'objectId': objectId }
        result = requests.post((BASE_URL + '/objects/search'), post_fields)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }
    # List
    def list(self):
        post_fields = { 'apiKey': self.apiKey, 'app': self.appId }
        result = requests.post((BASE_URL + '/objects/list'), post_fields)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # Search
    def search(self, keyValues):
        post_fields = { 'apiKey': self.apiKey, 'app': self.appId, 'keyValues': keyValues }
        result = requests.post((BASE_URL + '/objects/search'), post_fields)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }
