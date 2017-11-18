# -*- coding: utf-8 -*-
"""
    Python client for adPix API services
"""

import json
import os
import magic

import requests

GPU_API_URL = "http://gpuapi.snshine.in"
CPU_API_URL = "http://adpixapi.snshine.in"
MAX_BATCH_SIZE = 128

class adpixApp(object):
    def __init__(self, api_key, use_cpu=True):
        if use_cpu:
            self.BASE_URL = CPU_API_URL
        else:
            self.BASE_URL = GPU_API_URL
        self.api_key = api_key
        self.models = Models(self.api_key, self.BASE_URL)


class Models(object):
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.BASE_URL = base_url
        self.all_models = self._get_all()


    def _get_all(self):
        """
            Calls api and returns all the available models right now.
            Returns a list of model names.
        """
        models_result = requests.get(self.BASE_URL + "/api/v1/models")
        if models_result.status_code in [429]:
            raise UserError(models_result.json()["error"])
        all_models = models_result.json()["result"]

        return all_models


    def get(self, model_name):
        """ Loads the model on server side and returns Model() """
        if model_name not in self.all_models:
            raise UserError("Requested model_name is not found in available models!")

        params = "api_key=" + self.api_key + "&model_name=" + model_name
        load_models_result = requests.get(self.BASE_URL + "/api/v1/load_model?" + params)
        if load_models_result.status_code == 200:
            return Model(self.api_key, model_name, self.BASE_URL)
        elif load_models_result.status_code in [400, 403, 429]:
            raise UserError(load_models_result.json()["error"])
        else:
            print load_models_result.status_code, load_models_result.text
            raise ServerError("Problem loading the model on server side...  Printing server response!")


class Model(object):
    def __init__(self, api_key, model_name, base_url):
        self.api_key = api_key
        self.model_name = model_name
        self.BASE_URL = base_url
        self.mime = magic.Magic(mime=True)

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.model_name)


    def _upload(self, file_names):
        """ Uploads image file or image files """
        params = "api_key=" + self.api_key

        image_files = []
        for file_id, file_name in enumerate(file_names):
            image_files.append([str(file_id), [file_name, open(file_name, "rb"), "image/jpeg"]])

        upload_result = requests.post(self.BASE_URL + "/api/v1/upload?" + params, files=image_files)

        if upload_result.status_code == 201:
            return upload_result.json()
        elif upload_result.status_code in [400, 403, 429]:
            raise UserError(upload_result.json()["error"])
        else:
            print upload_result, upload_result.text
            raise ServerError("Problem uploading image to the server... Printing server response!")


    def predict_by_base64(self, imagebase64):
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
        """ Wrapper on top of predict_by_file_names """
        if not isinstance(file_name, str):
            raise UserError("file_name should be a str.")
        return self.predict_by_file_names([file_name])


    def predict_by_file_names(self, file_names):
        """
            Main method which does same as predict but uploads file
            rather than sending base64 string.

            If batch: expecting a list of file_names in place of file_name. Else a str of file_name
        """
        if not isinstance(file_names, list):
            raise UserError("file_names should be a list of file names.")
        if len(file_names) > MAX_BATCH_SIZE:
            raise UserError("Maximum batch size is {}. Given batch size: {}".format(MAX_BATCH_SIZE, len(file_names)))

        for file_pos, file_name in enumerate(file_names):
            if not os.path.exists(file_name):
                raise UserError("File path doesn't exists: {}. Position (0-indexed) in batch: {}".format(file_name, file_pos))
            elif not os.path.isfile(file_name):
                raise UserError("Path is not a file: {}. Position (0-indexed) in batch: {}".format(file_name, file_pos))
            elif self.mime.from_file(file_name) not in ["image/jpeg", "image/jpg"]:
                raise UserError("File's mimetype is not acceptable: {}. Position (0-indexed) in batch: {}".format(file_name, file_pos))

        upload_result = self._upload(file_names)
        server_file_names = upload_result["server_image_file_names"]

        params = "api_key=" + self.api_key + "&model_name=" + self.model_name + "&server_imgs=" + json.dumps(server_file_names)
        predict_result = requests.post(self.BASE_URL + "/api/v1/predict?" + params)

        if predict_result.status_code == 201:
            return predict_result.json()
        elif predict_result.status_code in [400, 403, 429]:
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
