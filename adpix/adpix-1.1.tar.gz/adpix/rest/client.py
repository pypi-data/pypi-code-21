# -*- coding: utf-8 -*-
"""
    Python client for adPix API services
"""

import json
import os

import requests

GPU_BASE_URL = "http://ec2-34-202-70-124.compute-1.amazonaws.com"
CPU_API_URL = "http://adpixapi.snshine.in"

class adpixApp(object):
    def __init__(self, api_key, debug=True):
        if debug:
            self.BASE_URL = CPU_API_URL
        else:
            self.BASE_URL = GPU_BASE_URL
        self.api_key = api_key
        self.models = Models(self.api_key, self.BASE_URL)


class Models(object):
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.BASE_URL = base_url


    def _get_all(self):
        """
            Calls api and returns all the available models right now.
            Returns a list of model names.
        """
        models_result = requests.get(self.BASE_URL + "/api/v1/models")
        all_models = models_result.json()["result"]

        return all_models


    def get(self, model_name):
        """ Loads the model on server side and returns Model() """
        all_models = self._get_all()
        if model_name not in all_models:
            raise UserError("Requested model_name is not found in available models!")

        params = "api_key=" + self.api_key + "&model_name=" + model_name
        load_models_result = requests.get(self.BASE_URL + "/api/v1/load_model?" + params)
        if load_models_result.status_code == 200:
            return Model(self.api_key, model_name, self.BASE_URL)
        elif load_models_result.status_code == 400:
            raise UserError(load_models_result.json()["error"])
        elif load_models_result.status_code == 403:
            raise UserError(load_models_result.json()["error"])
        else:
            print load_models_result.status_code, load_models_result.text
            raise ServerError("Problem loading the model on server side...  Printing server response!")


class Model(object):
    def __init__(self, api_key, model_name, base_url):
        self.api_key = api_key
        self.model_name = model_name
        self.BASE_URL = base_url


    def predict(self, imagebase64):
        """
            Main method which predicts/detects based on the image data.
            This method sends api_key, model_name, imagebase64 to get the output.
        """
        params = "api_key=" + self.api_key + "&model_name=" + self.model_name + "&imagebase64=" + imagebase64
        predict_result = requests.post(self.BASE_URL + "/api/v1/predict?" + params)
        if predict_result.status_code == 201:
            return predict_result.json()
        else:
            print predict_result, predict_result.text
            return None


    def predict_by_file_name(self, file_name):
        """
            Main method which does same as predict but uploads file
            rather than sending base64 string.
        """
        if not os.path.exists(file_name):
            raise UserError("File path doesn't exists!")
        elif not os.path.isfile(file_name):
            raise UserError("Provided local path is not a file!")

        params = "api_key=" + self.api_key + "&model_name=" + self.model_name
        with open(file_name, "rb") as img_file:
            predict_result = requests.post(self.BASE_URL + "/api/v1/predict?" + params, files={"file": (file_name, img_file),
                                                                                               "Content-Type": "image/jpeg"})

        if predict_result.status_code == 201:
            return predict_result.json()
        elif predict_result.status_code == 400:
            raise UserError(predict_result.json()["error"])
        elif predict_result.status_code == 403:
            raise UserError(predict_result.json()["error"])
        else:
            print predict_result, predict_result.text
            raise ServerError("Problem predicting image on the server side... Printing server response!")


class ServerError(Exception):
    """ Raised if got an unexpected server response """
    pass


class UserError(Exception):
    """ Raised for user side errors """
    pass
