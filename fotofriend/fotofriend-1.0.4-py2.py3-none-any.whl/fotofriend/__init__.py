import requests
import json
import os
import base64

#Python FotoFriend API

ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png'])
HTTP_SERVER = "fotofriendserver.us-west-2.elasticbeanstalk.com"

def login(username):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'username': username})
    response = requests.post("http://%s/login" % HTTP_SERVER, data = data, headers = headers)

    print("FOTO_FRIEND_LOGIN: Success")
    return response.json()

def uploadImage(fileObject, fileName, sessionUsername):
    if not checkFileExtension(fileName):
        print("FOTO_FRIEND_UPLOAD: Invalid file extenstion")
        uploadStatus = 0
    else:
        response = requests.post("http://%s/storeImage" % HTTP_SERVER, data=dict(file=base64.b64encode(fileObject), filename=fileName, username=sessionUsername))
        if response.status_code == 200:
            uploadStatus = 1

    print("FOTO_FRIEND_UPLOAD: Success")
    return uploadStatus

def deleteImage(imageUrl, sessionUsername):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'url': imageUrl, 'username': sessionUsername})
    response = requests.post("http://%s/deleteImage" % HTTP_SERVER, data = data, headers = headers)

    print("FOTO_FRIEND_DELETE: Success")
    return response.status_code

def filter(keywordsList, sessionUsername):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'keywords': keywordsList, 'username': sessionUsername})
    response = requests.post("http://%s/filter" % HTTP_SERVER, data = data, headers = headers)

    print("FOTO_FRIEND_FILTER: Success")
    return response.json()

#Check whether the filename extension is allowed 
def checkFileExtension(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS