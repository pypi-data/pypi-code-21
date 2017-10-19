import json
import requests

# Version: 0.1
BASE_URL = 'https://easyapi.io/api/v1'

class File:
    def __init__(self, apiKey, appId):
        self.apiKey = apiKey
        self.appId = appId

    # File upload
    # 1: file
    # 2: isPublic (Optional)
    # 3: tags (Optional)
    # 4: path (Optional)
    #
    # Ex. Easyapi.File.upload(open('file.txt','rb'), False)
    def upload(self, *args):
        if (len(args) == 0):
            return { 'success': False, 'message': 'Error: Invalid parameters' }
        fileBody = args[0]

        isPublic = False
        if (len(args) >= 2):
            isPublic = args[1]

        tags = []
        if (len(args) >= 3):
            typeStr = args[2]

        path = ''
        if (len(args) >= 4):
            path = args[3]

        files = { 'file': fileBody }
        post_fields = { 'apiKey': self.apiKey, 'app': self.appId, 'isPublic': isPublic, 'tags': tags, 'path': path }
        result = requests.post((BASE_URL + '/files/upload'), files=files, data=post_fields)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # List
    # 1. path
    def list(self, *args):
        path = ''
        if (len(args) == 1):
            path = args[0]

        post_fields = { 'apiKey': self.apiKey, 'app': self.appId, 'path': path }
        result = requests.post((BASE_URL + '/files/list'), post_fields)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # Get
    # 1. File Id
    def get(self, fileId):
        post_fields = { 'apiKey': self.apiKey, 'app': self.appId, 'fileId': fileId }
        result = requests.post((BASE_URL + '/files/get'), post_fields)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # Request Key
    # 1. File id
    def requestKey(self, fileId):
        post_fields = { 'apiKey': self.apiKey, 'app': self.appId, 'fileId': fileId }
        result = requests.post((BASE_URL + '/files/request/key'), post_fields)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # Delete
    # 1. File id
    def delete(self, fileId):
        post_fields = { 'apiKey': self.apiKey, 'app': self.appId, 'fileId': fileId }
        result = requests.post((BASE_URL + '/files/delete'), post_fields)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # Body
    # No API key or App Id
    # 1. fileId
    # 2. requestKey
    # 3. download
    def getFileBody(self, fileId, requestKey, download):
        post_fields = { 'apiKey': self.apiKey, 'app': self.appId, 'fileId': fileId, 'requestKey': requestKey, 'download': download }
        result = requests.post((BASE_URL + '/files/body'), post_fields)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }
