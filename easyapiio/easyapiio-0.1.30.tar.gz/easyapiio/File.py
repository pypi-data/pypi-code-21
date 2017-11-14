import json
import requests

# Version: 0.1
BASE_URL = 'https://api.easyapi.io/v1'

class File:
    def __init__(self, apiKey, appId):
        self.apiKey = apiKey
        self.appId = appId

    def getVersion(self):
        return '0.1.30'

    def getAPIKey(self):
        return self.apiKey

    def getAppId(self):
        return self.appId

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

        tags = [];
        if (len(args) >= 3):
            tags = args[2]

        # TODO - on a bus check if you can just do += in Python. On bus no
        # internet.
        tagsStr = ''
        for tag in tags:
            if (tagsStr != ''):
                tagsStr = tagsStr + ','
            tagsStr = tagsStr + tag

        path = ''
        if (len(args) >= 4):
            path = args[3]

        files = { 'file': fileBody }
        headers = { 'Authorization': ('Bearer ' + str(self.apiKey)) }
        post_fields = {
            'appId': self.appId,
            'isPublic': isPublic,
            'tags': tagsStr,
            'path': path,
            'sdkVersion': self.getVersion(),
            'sdk': 'python-sdk'
        }
        result = requests.post('https://api.easyapi.io/v1/files/upload', files=files, data=post_fields, headers=headers)
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

        headers = { 'Content-type': 'application/json', 'Authorization': ('Bearer ' + str(self.apiKey)) }
        post_fields = {
            'appId': self.appId,
            'path': path,
            'sdkVersion': self.getVersion(),
            'sdk': 'python-sdk'
        }
        result = requests.post('https://api.easyapi.io/v1/files/list', json=post_fields, headers=headers)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # Get
    # 1. File Id
    def get(self, fileId):
        headers = { 'Content-type': 'application/json', 'Authorization': ('Bearer ' + str(self.apiKey)) }
        post_fields = {
            'appId': self.appId,
            'fileId': fileId,
            'sdkVersion': self.getVersion(),
            'sdk': 'python-sdk'
        }
        result = requests.post('https://api.easyapi.io/v1/files/get', json=post_fields, headers=headers)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # Request Key
    # 1. File id
    def getRequestKey(self, fileId):
        headers = { 'Content-type': 'application/json', 'Authorization': ('Bearer ' + str(self.apiKey)) }
        post_fields = {
            'appId': self.appId,
            'fileId': fileId,
            'sdkVersion': self.getVersion(),
            'sdk': 'python-sdk'
        }
        result = requests.post('https://api.easyapi.io/v1/files/request/key', json=post_fields, headers=headers)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # Delete
    # 1. File id
    def delete(self, fileId):
        headers = { 'Content-type': 'application/json', 'Authorization': ('Bearer ' + str(self.apiKey)) }
        post_fields = {
            'appId': self.appId,
            'fileId': fileId,
            'sdkVersion': self.getVersion(),
            'sdk': 'python-sdk'
        }
        result = requests.post('https://api.easyapi.io/v1/files/delete', json=post_fields, headers=headers)
        if (result.status_code == 200):
            return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    # Body
    # No API key or App Id
    # 1. fileId
    # 2. requestKey
    # 3. download
    def getFileBody(self, requestKey, download):
        headers = { 'Content-type': 'application/json' }
        fields = {
            'requestKey': requestKey,
            'download': download,
            'sdkVersion': self.getVersion(),
            'sdk': 'python-sdk'
        }
        result = requests.get('https://api.easyapi.io/v1/files/body', params=fields, headers=headers)
        if (result.status_code == 200):
            if (download == True):
                return result.text
            else:
                return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }

    def getPublicFileBody(self, fileId, download):
        headers = { 'Content-type': 'application/json' }
        fields = {
            'fileId': fileId,
            'download': download,
            'sdkVersion': self.getVersion(),
            'sdk': 'python-sdk'
        }
        result = requests.get('https://api.easyapi.io/v1/files/body', params=fields, headers=headers)
        if (result.status_code == 200):
            if (download == True):
                return result.text
            else:
                return result.json()
        else:
            return { 'statusCode': result.status_code, 'success': False, 'message': 'Status error.' }
