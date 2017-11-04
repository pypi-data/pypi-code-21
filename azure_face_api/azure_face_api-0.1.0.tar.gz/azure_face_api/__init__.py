"""
API wrapper for Azure Face API
Author: Thomas Ashish Cherian
https://github.com/PandaWhoCodes/pyautocorrect
"""

import requests
import json


class face():
    def set_key(self, key):
        self.subscription_key = key

    def make_request(self, image):
        """
        Makes request to the azure face api
        :param image: the URL or local image
        :return:
        """
        try:
            if len(self.subscription_key) > 5:
                pass
        except:
            return {"error": "set the subcription key first"}
        self.url = 'https://westcentralus.api.cognitive.microsoft.com'
        self.headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': self.subscription_key,
        }
        self.local = True
        # Request parameters.
        params = {
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
        }
        if "http" in image:
            self.body = {'url': image}
            self.headers["Content-Type"] = 'application/json'
            self.local = False
        else:
            f = open(image, "rb")
            body = f.read()
            f.close()
            self.body = body
        try:
            if self.local:
                response = requests.request('POST', self.url + '/face/v1.0/detect', data=self.body,
                                            headers=self.headers,
                                            params=params)
                parsed = json.loads(response.text)
                return parsed
            else:
                response = requests.request('POST', self.url + '/face/v1.0/detect', json=self.body, data=None,
                                            headers=self.headers,
                                            params=params)
                parsed = json.loads(response.text)
                return parsed
        except Exception as e:
            print('Error:')
            print(e)
