# coding: utf-8

"""
    stylelens-detect

    This is a API document for Object Detection on fashion items\"

    OpenAPI spec version: 0.0.1
    Contact: devops@bluehack.net
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

# import models into sdk package
from .models.box_array import BoxArray
from .models.box_object import BoxObject
from .models.boxes_array import BoxesArray
from .models.detect_objects_response import DetectObjectsResponse
from .models.detect_objects_response_data import DetectObjectsResponseData

# import apis into sdk package
from .apis.detect_api import DetectApi

# import ApiClient
from .api_client import ApiClient

from .configuration import Configuration

configuration = Configuration()
